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

import exceptions
import time

from cueclient.v1 import client
from keystoneclient.auth.identity import v2 as ks_v2
import keystoneclient.openstack.common.apiclient.exceptions as ks_exceptions
from keystoneclient import session as ks_session
from rally.common import log as logging
from rally.plugins.openstack import scenario
from rally.task.scenarios import base
from rally.task import utils as task_utils

import os

LOG = logging.getLogger(__name__)


class CueScenario(scenario.OpenStackScenario):
    """Base class for Cue scenarios with basic atomic actions."""

    @base.atomic_action_timer("cue.clusters.list")
    def _list_clusters(self, cueclient=None):
        """Returns user clusters list."""
        cue_client = cueclient or self._get_cue_client()
        return cue_client.clusters.list()

    @base.atomic_action_timer("cue.clusters.create")
    def _create_cluster(self, name, flavor, size, network_id,
                        volume_size=0, cueclient=None):
        """Submit request to create cue cluster.

        Will return immediate response from Cue, does not wait until "ACTIVE"
        state.

        :param name: str, cluster name
        :param flavor: int, flavor ID for VM instance(s)
        :param size: int, size of cluster in number of VMs
        :param network_id: UUID, user's network to connect VMs to
        :param volume_size: int, volume size for VM instance(s)
        :returns: new cue cluster details
        """
        cluster_name = name or self._generate_random_name('rally_cue_cluster_')
        cue_client = cueclient or self._get_cue_client()
        return cue_client.clusters.create(name=cluster_name, nic=network_id,
                                          flavor=flavor, size=size,
                                          volume_size=volume_size)

    @base.atomic_action_timer("cue.clusters.get")
    def _get_cluster(self, id, cueclient=None):
        """Retrieves a cluster record by cluster id.

        :param id: int, cluster id
        :return: cluster details
        """
        cue_client = cueclient or self._get_cue_client()
        return cue_client.clusters.get(cluster_id=id)

    @base.atomic_action_timer("cue.clusters.delete")
    def _delete_cluster(self, id, cueclient=None):
        """Submits request to Delete a cluster.

        :param id: int, cluster id
        :return: response code
        """
        cue_client = cueclient or self._get_cue_client()
        return cue_client.clusters.delete(cluster_id=id)

    def _get_cue_client(self):
        """Retrieve an instance of Cue Client.

        :return: cue client
        """
        keystone_client = self.clients("keystone")
        auth = ks_v2.Token(
            keystone_client.auth_url,
            keystone_client.auth_token,
            tenant_id=keystone_client.tenant_id,
            tenant_name=keystone_client.tenant_name,
            trust_id=keystone_client.trust_id
        )
        session = ks_session.Session(auth=auth)
        cue_client = client.Client(session=session)
        return cue_client

    def _verify_cluster(self, ref_cluster, cmp_cluster):
        """Verifies basic values between two cluster dictionaries

        :param ref_cluster: reference cluster
        :param cmp_cluster: comparison cluster
        :return:
        """
        match = True
        if ref_cluster['flavor'] != cmp_cluster['flavor']:
            LOG.debug("Flavor do not match, ref: %s cmp: %s" %
                      (ref_cluster['flavor'], cmp_cluster['flavor']))
            match = False

        if ref_cluster['size'] != cmp_cluster['size']:
            LOG.debug("Size do not match, ref: %s cmp: %s" %
                      (ref_cluster['size'], cmp_cluster['size']))
            match = False

        if ref_cluster['network_id'] != cmp_cluster['network_id'][0]:
            LOG.debug("Network ID do not match, ref: %s cmp: %s" %
                      (ref_cluster['network_id'], cmp_cluster['network_id']))
            match = False

        if ref_cluster['volume_size'] != cmp_cluster['volume_size']:
            LOG.debug("Volume size do not match, ref: %s cmp: %s" %
                      (ref_cluster['volume_size'], cmp_cluster['volume_size']))
            match = False

        return match

    @base.atomic_action_timer("wait.for.delete")
    def _wait_for_cluster_delete(self, cluster_id, timeout=300,
                                 check_interval=1):
        """Waits for specified cluster has been deleted.

        A cluster is deleted when the cluster get operation fails to retrieve
        the cluster record.

        :param cluster_id: int, cluster id.
        """
        start_time = time.time()
        while True:
            try:
                self._get_cluster(cluster_id)
            except ks_exceptions.NotFound:
                break
            if time.time() - start_time > timeout:
                raise exceptions.Exception("Delete cluster timed out")
            time.sleep(check_interval)

    @base.atomic_action_timer("wait.for.status.changes")
    def _wait_for_status_change(self, cluster_id, final_status, timeout=300,
                                check_interval=1):
        """Waits for specified change in cluster status.

        Will wait until cluster status changes to a specified status within
        timeout period.

        :param: cluster_id: uuid, cluster id
        :param final_status: str, final cluster status
        :param timeout: int, max time to check for status change
        :param check_interval: int, interval to check status changes in
        """

        start_time = time.time()
        while True:
            cluster = self._get_cluster(cluster_id)
            current_status = cluster['status']
            if current_status == final_status:
                return cluster
            time.sleep(check_interval)
            if time.time() - start_time > timeout:
                self._delete_cluster(cluster_id)
                raise exceptions.Exception("Timeout while waiting for status "
                                           "change to %s.", final_status)

    def _create_network(self, neutron_client, network_name):
        """Create neutron network

        :param neutron_client: neutron client
        :param network_name: str, name of the new network
        :return: router, subnet , network
        """
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

    def _create_cue_cluster(self, cluster_name, size, network_id,
                            cluster_flavor, cluster_volume_size,
                            cluster_timeout, cluster_check_interval):
        """Create cue cluster

        Will wait until the cluster goes "ACTIVE" and returns the cue object.

        :param cluster_name: str, cluster name
        :param size: int, size of cluster in number of VMs
        :param network_id: UUID, user's network to connect VMs to
        :param cluster_flavor: int, flavor for VM instance
        :param cluster_volume_size: int, volume size for VM instance
        :param cluster_timeout: int, max time to check for status change
        :param cluster_check_interval: int, interval to check status change
        :return: new cue cluster
        """
        cluster_name = cluster_name or self._generate_random_name(
            'rally_cue_cluster_')
        cluster_dict = {'name': cluster_name,
                        'flavor': cluster_flavor,
                        'size': size,
                        'network_id': network_id,
                        'volume_size': cluster_volume_size}

        # Submit request to create cluster and wait for ACTIVE status
        LOG.info("Creating cue cluster")
        cluster = self._create_cluster(**cluster_dict)

        cluster = self._wait_for_status_change(cluster['id'], 'ACTIVE',
                                               cluster_timeout,
                                               cluster_check_interval)
        assert self._verify_cluster(cluster_dict, cluster), (
            "Invalid Created Cluster")

        LOG.info("Cluster created!")
        return cluster

    def _create_nova_vm(self, nova_client, flavor, image, keypair,
                        server_name, sec_group_name, nova_server_boot_timeout,
                        **kwargs):
        """Create nova instance

        :param nova_client: nova client
        :param flavor: int, flavor for VM instance
        :param image: str/uuid, image_name/image_id of the new instance
        :param keypair: str, key-pair to allow ssh
        :param server_name: str, name for VM instance
        :param nova_server_boot_timeout: int, max time for instance to go
        active
        :return: new nova instance
        """
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
        task_utils.wait_for(server,
                                 is_ready=task_utils.
                                 resource_is("ACTIVE"),
                                 update_resource=task_utils.
                                 get_from_manager(),
                                 timeout=nova_server_boot_timeout)

        # assert if instance is 'active'
        assert('ACTIVE' == server.status), (
            "The instance is not in ACTIVE state")
        return server

    def _add_floating_ip(self, nova_client, server):
        """Associates floating-ip to a server

        :param nova_client: nova client
        :param server: nova instance
        :return: associated floating ip
        """
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

    def _delete_server(self, nova_id):
        """Delete nova instance

        :param nova_id: instance id to delete
        :return:
        """
        # Remove rally key-pair
        nova_client = self.clients("nova")

        vm_list = nova_client.servers.list()
        for vm in vm_list:
            if nova_id == vm.id:
                server = vm
                sec_group_name = vm.security_groups[0]['name']
                server_id = vm.id
                server_key_name = vm.key_name
                break

        LOG.info("Deleting nova instance: %s", server_id)
        nova_client.servers.delete(server_id)

        LOG.info("Waiting for instance to get deleted")
        task_utils.wait_for_delete(server,
                                        update_resource=task_utils.
                                        get_from_manager())

        # delete sec-group
        for secgroup in nova_client.security_groups.list():
                if secgroup.name == sec_group_name:
                    LOG.info("Deleting sec-group: %s", sec_group_name)
                    nova_client.security_groups.delete(secgroup.id)

        # delete key-pair
        for key_pair in nova_client.keypairs.list():
            if key_pair.name == server_key_name:
                LOG.info("Deleting key-pair: %s", server_key_name)
                nova_client.keypairs.delete(key_pair.id)

    def _delete_network(self, network_tuple):
        """Delete neutron network.

        :param network_tuple: tuple, router, network and subnet to delete
        :return
        """
        neutron_client = self.clients("neutron")
        router = network_tuple[0]
        network = network_tuple[1]
        subnet = network_tuple[2]

        try:
            # delete interface subnet-router
            LOG.info("Deleting router interface")
            neutron_client.remove_interface_router(
                router["router"]["id"], {"subnet_id": subnet['subnet']["id"]})

            # delete ports associated with interface
            LOG.info("Deleting ports")
            port_list = neutron_client.list_ports()["ports"]
            for port in port_list:
                neutron_client.delete_port(port["id"])

            # delete router
            LOG.info("Deleting router")
            neutron_client.delete_router(router["router"]["id"])

            # delete network
            LOG.info("Deleting network")
            neutron_client.delete_network(network["network"]["id"])

        except Exception as err:
            LOG.exception(err)

    def _delete_key_file(self, key_file):
        """Delete ssh key file

        :param key_file: path to ssh key file
        :return:
        """
        LOG.debug("Deleting rally key file")
        if os.path.exists(key_file):
            os.remove(key_file)
