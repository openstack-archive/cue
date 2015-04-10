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
from rally.benchmark.scenarios import base
from rally.common import log as logging

LOG = logging.getLogger(__name__)


class CueClusters(cue_utils.CueScenario):
    """Benchmark Rally scenarios for Cue."""

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
            networks = networks["networks"]
            for network in networks:
                if network["name"] == "private":
                    network_id = network["id"]
                    break

        # Submit request to create cluster and wait for ACTIVE status
        cluster = self._create_cluster(name=name, flavor=flavor,
                                       size=size, network_id=network_id,
                                       volume_size=volume_size)
        self._wait_for_status_change(cluster['id'], cluster['status'],
                                     'ACTIVE', timeout, check_interval)

        self.sleep_between(min_sleep, max_sleep)

        # Submit request to delete cluster and wait for cluster delete
        self._delete_cluster(cluster["id"])
        self._wait_for_cluster_delete(cluster["id"], timeout, check_interval)
