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
from rally.benchmark.scenarios import base
from rally.common import log as logging

LOG = logging.getLogger(__name__)


class CueScenario(base.Scenario):
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

    def _get_cue_client(self, auth_url=None, username=None, password=None,
                        tenant_name=None):
        """Retrieve an instance of Cue Client.

        Will use sourced environment variables if explicit values are not
        provided

        :param auth_url: str, authentication url to keystone
        :param username: str, OpenStack username
        :param password: str, OpenStack password
        :param tenant_name: str, OpenStack tenant name
        :return:
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
