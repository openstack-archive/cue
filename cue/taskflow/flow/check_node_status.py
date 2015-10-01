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

import cue.taskflow.task as cue_tasks
import os_tasklib.common as os_common


def check_node_status(cluster_id, node_number, node_id):
    """Check Node Status factory function

    This factory function deletes a flow for deleting a node of a cluster.

    :param cluster_id: Unique ID for the cluster that the node is part of.
    :type cluster_id: string
    :param node_number: Cluster node # for the node being deleted.
    :type node_number: number
    :param node_id: Unique ID for the node.
    :type node_id: string
    :return: A flow instance that represents the workflow for deleting a
             cluster node.
    """
    flow_name = "check cluster %s status on node %d" % (cluster_id,
                                                        node_number)
    node_name = "cluster[%s].node[%d]" % (cluster_id, node_number)

    # Extract management ip
    extract_mgmt_ip = lambda node: node['mgmt_ip']

    flow = linear_flow.Flow(flow_name)
    flow.add(
        cue_tasks.GetNode(
            name="Get Node %s" % node_name,
            inject={'node_id': node_id},
            provides="node_%d" % node_number),
        os_common.Lambda(
            extract_mgmt_ip,
            name="extract management ip %s" % node_name,
            rebind={'node': "node_%d" % node_number},
            provides="vm_mgmt_ip_%d" % node_number),
        cue_tasks.GetRabbitClusterStatus(
            name="get RabbitMQ status",
            rebind={'vm_ip': "vm_mgmt_ip_0"},
            provides={"node_status_%d" % node_number},
            inject={'proto': 'http'}),
        #TODO(abitha): Update node status
    )
    return flow
