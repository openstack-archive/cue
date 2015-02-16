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


def create_cluster(cluster_id, cluster_size):
    """Create Cluster flow factory function

    This factory function uses :func:`cue.taskflow.flow.create_cluster_node` to
    create a multi node cluster.

    :param cluster_id: A unique ID assigned to the cluster being created
    :type cluster_id: string
    :param cluster_size: The number of nodes in the cluster
    :type cluster_size: number
    :return: A flow instance that represents the workflow for creating a
             cluster
    """
    flow = linear_flow.Flow("creating cluster %s" % cluster_id)
    sub_flow = unordered_flow.Flow("create VMs")
    for i in range(cluster_size):
        sub_flow.add(create_cluster_node.create_cluster_node(cluster_id, i))

    flow.add(sub_flow)

    return flow
