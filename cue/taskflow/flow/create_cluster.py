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

import taskflow.patterns.linear_flow as linear_flow
import taskflow.patterns.unordered_flow as unordered_flow

from cue.taskflow.flow import create_cluster_node
import cue.taskflow.task as cue_task


def create_cluster(cluster_id, cluster_size):
    flow = linear_flow.Flow("creating cluster %s" % cluster_id)
    sub_flow = unordered_flow.Flow("create VMs")
    for i in range(cluster_size):
        sub_flow.add(create_cluster_node(cluster_id, i))

    flow.add(sub_flow)

    return flow
