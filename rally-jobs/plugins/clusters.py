# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import time

import cue_utils
from oslo_log import log as logging
from rally.benchmark.scenarios import base
from rally.benchmark import types as types
from rally.benchmark import utils as benchmark_utils
from rally.common import sshutils

import os
import stat

LOG = logging.getLogger(__name__)


class CueClusters(cue_utils.CueScenario):
    """Benchmark Rally scenarios for Cue."""
    SUBNET_IP_VERSION = 4

    @base.scenario()
    def create_and_delete_cluster(self, name=None, flavor="8795",
                                  size=1, network_id=None, volume_size=0,
                                  timeout=300, check_interval=1, min_sleep=0,
                                  max_sleep=0):
        """Creates a new cue cluster.

        1. If Network_id is not provided, network id will be retrieved from
           the private network.
        2. Submit request to create cluster
        3. Wait until cluster goes ACTIVE
            3.1 If timeout, cluster is deleted
        4. Submit request to delete cluster
        5. Wait until cluster is deleted

        :param name: str, cluster name
        :param flavor: int, flavor ID for VM instance(s)
        :param size: int, size of cluster in number of VMs
        :param network_id: UUID, user's network to connect VMs to
        :param volume_size: int, volume size for VM instance(s)
        :returns: new cue cluster details
        """
        # Retrieve appropriate network id if not provided
        if not network_id:
            networks = self.admin_clients("neutron").list_networks()
            networks = networks['networks']
            for network in networks:
                if network['name'] == "private":
                    network_id = network['id']
                    break

        cluster_dict = {'name': name,
                        'flavor': flavor,
                        'size': size,
                        'network_id': network_id,
                        'volume_size': volume_size}
        # Submit request to create cluster and wait for ACTIVE status
        cluster = self._create_cluster(**cluster_dict)
        cluster_active = self._wait_for_status_change(cluster['id'], 'ACTIVE',
                                                      timeout, check_interval)
        assert self._verify_cluster(cluster_dict, cluster_active), (
            "Invalid Created Cluster")

        self.sleep_between(min_sleep, max_sleep)

        # Submit request to delete cluster and wait for cluster delete
        self._delete_cluster(cluster['id'])
        self._wait_for_cluster_delete(cluster['id'], timeout, check_interval)

    @types.set(image=types.ImageResourceType,
               flavor=types.FlavorResourceType)
    @base.scenario()
    def boot_and_ssh_vm(self, image, flavor, network_id=None, name="rally_vm",
                        cluster_name="rally_cluster", cluster_flavor="8795",
                        size=1, cluster_volume_size=0, cluster_timeout=300,
                        cluster_check_interval=1, **kwargs):
        """Boot a nova instance , create a cue instance, ssh from nova instance

         to cue instance and run a command on it.

        :param image: str, image name for server creation
        :param flavor: str, flavor for server creation
        :param network_id: str, network id for server creation
        :param name: str, server name
        :param cluster_name: str, cluster name
        :param cluster_flavor: str, cluster flavor
        :param size: int, cluster size
        :param cluster_volume_size: int, cluster volume size
        :param cluster_timeout: int, time out seconds for cluster to go active
        :param cluster_check_interval: int, check interval seconds
        :param kwargs: other optional parameters to initialize the server
        """
        server_name = name or self._generate_random_name()
        nova_server_boot_timeout = 60 * 5
        network_name = "rally_network"
        sec_group_name = "rally_sec_group"
        key_name = "rally_keypair"
        key_file_name = '/tmp/' + key_name
        cluster = None
        server = None

        neutron_client = self.clients("neutron")
        nova_client = self.clients("nova")

        try:
            # create a key-pair
            LOG.info("Adding new keypair")
            keypair = nova_client.keypairs.create(key_name)
            f = open(key_file_name, 'w')
            os.chmod(key_file_name, stat.S_IREAD | stat.S_IWRITE)
            f.write(keypair.private_key)
            f.close()

            if not network_id:
                # create new network
                test_network = self._create_network(neutron_client,
                                                    network_name)
            network_id = test_network[1]["network"]["id"]

            # create cue_cluster
            cluster = self._create_cue_cluster(cluster_name, size, network_id,
                                               cluster_flavor,
                                               cluster_volume_size,
                                               cluster_timeout,
                                               cluster_check_interval)

            # assign network_id argument
            kwargs["nics"] = [{"net-id": network_id}]
            server = self._create_nova_vm(nova_client, flavor, image, keypair,
                                          server_name, sec_group_name,
                                          nova_server_boot_timeout, **kwargs)

            LOG.info("Adding floating ip")
            floating_ip = self._add_floating_ip(nova_client, server)

            # ssh instance
            LOG.info("SSHing to instance")
            ssh = sshutils.SSH("ubuntu", floating_ip,
                               key_filename=key_file_name)
            ssh.wait()

            # run a command
            endpoint = cluster.end_points[0]
            uri = endpoint['uri'].split(':')
            LOG.info("Telnet to rabbitmq-cluster instance")
            status, stdout, stderr = ssh.execute("nc -zv {0} {1}".
                                                 format(uri[0], uri[1]))
            if status:
                raise Exception("Command failed with non-zero status.")

            LOG.info(stderr)
            assert('succeeded' in stderr), "Telnet assert failed"

        except Exception as err:
            LOG.exception(err)

        # cleanup - delete cluster, server, network and key file
        finally:
            if cluster is not None:
                self._delete_cluster(cluster['id'])
                self._wait_for_cluster_delete(cluster['id'], cluster_timeout,
                                              cluster_check_interval)

            if server is not None:
                self._delete_server(server.id)

            if test_network is not None:
                self._delete_network(test_network)

            self._delete_key_file(key_file_name)

    def _create_network(self, neutron_client, network_name):
        # create network
        LOG.info("Adding new network: %s", network_name)
        network_create_args = {"name": network_name}
        rally_network = neutron_client.create_network(
            {"network": network_create_args})

        time.sleep(3)
        # create subnet
        network_id = rally_network["network"]["id"]
        subnet_name = rally_network["network"]["name"] + "_subnet"
        LOG.info("Adding subnet: %s", subnet_name)
        subnet_create_args = {"name": subnet_name,
                              "cidr": "10.2.0.0/24",
                              "network_id": network_id,
                              "ip_version": self.SUBNET_IP_VERSION}
        rally_subnet = neutron_client.create_subnet(
            {"subnet": subnet_create_args})

        # create router and connect external gateway to public network
        router_name = rally_network["network"]["name"] + "_router"
        router_create_args = {}
        for network in neutron_client.list_networks()['networks']:
            if network.get("router:external"):
                external_network = network
                gw_info = {"network_id": external_network["id"]}
                router_create_args = {"name": router_name,
                                      "external_gateway_info": gw_info
                                      }
                break
        LOG.info("Adding router: %s", router_name)
        rally_router = neutron_client.create_router(
            {"router": router_create_args})

        # create router interface - connect subnet to it
        LOG.info("Adding router interface")
        neutron_client.add_interface_router(
            rally_router['router']["id"],
            {"subnet_id": rally_subnet["subnet"]["id"]})

        return rally_router, rally_network, rally_subnet

    def _create_cue_cluster(self, name, size, network_id, flavor, volume_size,
                            timeout, check_interval):
        cluster_dict = {'name': name,
                        'flavor': flavor,
                        'size': size,
                        'network_id': network_id,
                        'volume_size': volume_size}

        # Submit request to create cluster and wait for ACTIVE status
        LOG.info("Creating cue cluster")
        cluster = self._create_cluster(**cluster_dict)

        cluster = self._wait_for_status_change(cluster['id'], 'ACTIVE',
                                               timeout, check_interval)
        assert self._verify_cluster(cluster_dict, cluster), (
            "Invalid Created Cluster")

        LOG.info("Cluster created!")
        return cluster

    def _create_nova_vm(self, nova_client, flavor, image, keypair,
                        server_name, sec_group_name, nova_server_boot_timeout,
                        **kwargs):
        secgroup_found = False
        # add sec-group
        sec_groups = nova_client.security_groups.list()
        for sec in sec_groups:
            if sec.name == sec_group_name:
                secgroup_found = True
                secgroup = sec
                LOG.info("Security group already present")
                break
        if not secgroup_found:
            LOG.info("Adding new security group")
            secgroup = nova_client.security_groups.create(sec_group_name,
                                                          sec_group_name)
            # add new rule
            nova_client.security_group_rules.create(secgroup.id,
                                                    from_port=22,
                                                    to_port=22,
                                                    ip_protocol="tcp",
                                                    cidr="0.0.0.0/0")

        # boot new nova instance
        LOG.info("Booting new instance: %s", server_name)
        server = nova_client.servers.create(server_name,
                                            image=image,
                                            flavor=flavor,
                                            key_name=keypair.name,
                                            security_groups=[secgroup.id],
                                            **kwargs)

        # wait for instance to become active
        LOG.info("Waiting for instance to become active")
        benchmark_utils.wait_for(server,
                                 is_ready=benchmark_utils.
                                 resource_is("ACTIVE"),
                                 update_resource=benchmark_utils.
                                 get_from_manager(),
                                 timeout=nova_server_boot_timeout)

        # assert if instance is 'active'
        assert('ACTIVE' == server.status), (
            "The instance is not in ACTIVE state")
        return server

    def _add_floating_ip(self, nova_client, server):
        # associate floating-ip to the active instance
        floating_ip = None
        fip_list = nova_client.floating_ips.list()
        for fip in fip_list:
            if fip.instance_id is None:
                floating_ip = fip.ip
                break
        if floating_ip is None:
            LOG.info("Creating new floating ip")
            fp = nova_client.floating_ips.create()
            floating_ip = fp.ip
        LOG.info("Associating floating ip: %s", floating_ip)
        nova_client.servers.add_floating_ip(server.id, floating_ip)

        return floating_ip