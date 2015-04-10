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

import os

from cueclient.v1 import client
import keystoneclient
from rally.benchmark.scenarios import base
from rally.common import log as logging

LOG = logging.getLogger(__name__)

auth = keystoneclient.auth.identity.v2.Password(
    auth_url=os.environ['OS_AUTH_URL'],
    username=os.environ['OS_USERNAME'],
    password=os.environ['OS_PASSWORD'],
    tenant_name=os.environ['OS_TENANT_NAME']
)
session = keystoneclient.session.Session(auth=auth)
cue_client = client.Client(session=session)


class CueScenario(base.Scenario):
    """Base class for Cue scenarios with basic atomic actions."""

    @base.atomic.action_timer("cue.clusters.list")
    def _list_clusters(self):
        """Returns user clusters list."""
        return cue_client.clusters.list()

    @base.atomic.action_timer("cue.clusters.create")
    def _create_cluster(self, name, flavor, size, network_id,
                        volume_size=0):
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
        return cue_client.clusters.create(name=name, nic=network_id,
                                          flavor=flavor, size=size,
                                          volume_size=volume_size)

    @base.atomic.action_timer("cue.clusters.get")
    def _get_cluster(self, id):
        """ Retrieves a cluster record by cluster id.

        :param id: int, cluster id
        :return: cluster details
        """
        return cue_client.clusters.get(cluster_id=id)

    @base.atomic.action_timer("cue.clusters.delete")
    def _delete_cluster(self, id):
        """ Submits request to Delete a cluster.

        :param id: int, cluster id
        :return: response code
        """
        return cue_client.clusters.delete(cluster_id=id)