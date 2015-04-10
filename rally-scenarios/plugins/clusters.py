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
    def create_and_verify_cluster(self, name="cluster_0", flavor=8795, size=1,
                                  network_id=0, volume_size=0):
        """Creates a new cue cluster.

        1. If Network_id is not provided, network id will be retrieved from
           the private network
        2. Submit request to create cluster
        3. Wait until cluster goes ACTIVE
        """
        LOG.debug("Submit request to create cue cluster")
        cluster = self._create_cluster(name=name, flavor=flavor, size=size,
                                       network_id=network_id,
                                       volume_size=volume_size)
        LOG.debug("Cue cluster create response:\n%s", cluster)