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

import cue_utils

from rally.common import logging
from rally.common import sshutils
from rally.plugins.openstack import scenario
from rally.task import types as types

import os
import stat

LOG = logging.getLogger(__name__)


class CueClusters(cue_utils.CueScenario):
    """Task Rally scenarios for Cue."""
    SUBNET_IP_VERSION = 4

    @scenario.configure(context={"admin_cleanup": ["neutron"]})
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
    @scenario.configure(context={"cleanup": ["nova", "neutron"]})
    def create_verify_and_delete_cluster(self, image, flavor, network_id=None,
                                         cluster_name=None,
                                         cluster_flavor="8795", size=1,
                                         cluster_volume_size=0,
                                         cluster_timeout=300,
                                         cluster_check_interval=1, **kwargs):
        """Boot a nova instance , create a cue instance, ssh from nova instance

         to cue instance and run a command on it.

        :param image: str, image name for server creation
        :param flavor: str, flavor for server creation
        :param network_id: str, network id for server creation
        :param cluster_name: str, cluster name
        :param cluster_flavor: str, cluster flavor
        :param size: int, cluster size
        :param cluster_volume_size: int, cluster volume size
        :param cluster_timeout: int, time out seconds for cluster to go active
        :param cluster_check_interval: int, check interval seconds
        :param kwargs: other optional parameters to initialize the server
        """
        server_name = self.generate_random_name()
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
            rabbitmq_username = "rabbitmq"
            rabbitmq_password = "passowrd"

            # create cue_cluster
            cluster = self._create_cue_cluster(cluster_name, size, network_id,
                                               cluster_flavor,
                                               cluster_volume_size,
                                               cluster_timeout,
                                               cluster_check_interval,
                                               'plain', rabbitmq_username,
                                               rabbitmq_password)

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

            # run rabbitmq_test script
            endpoint = cluster.endpoints[0]
            uri = endpoint['uri'].split(':')
            rabbitmq_file = "/opt/rabbitmq_test.py"

            LOG.info("Running rabbitmq-test script")
            LOG.info('Testing for error when using invalid password')
            status, stdout, stderr = ssh.execute(
                "python {0} -H {1} -P {2} -u {3} -p {4}".
                format(rabbitmq_file, uri[0], uri[1], rabbitmq_username,
                       "invalid"))
            assert(status != 0), "Expected an error due to invalid password"

            LOG.info('Testing using valid rabbitmq credentials')
            status, stdout, stderr = ssh.execute(
                "python {0} -H {1} -P {2} -u {3} -p {4}".
                format(rabbitmq_file, uri[0], uri[1], rabbitmq_username,
                       rabbitmq_password))
            assert(status == 0), "Expected success"

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
