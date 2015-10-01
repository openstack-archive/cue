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

from cue.db.sqlalchemy import models
import cue.taskflow.task as cue_tasks
import os_tasklib.common as os_common


def check_node_status(cluster_id, node_number, node_id):
    """Check Node Status factory function

    This factory function check cluster status flow on each node of a cluster.

    :param cluster_id: Unique ID for the cluster that the node is part of.
    :type cluster_id: string
    :param node_number: Cluster node # for the node being deleted.
    :type node_number: number
    :param node_id: Unique ID for the node.
    :type node_id: string
    :return: A flow instance that represents the workflow for checking cluster
             cluster status on a node.
    """

    flow_name = "check cluster %s status on node %d" % (cluster_id,
                                                        node_number)
    node_name = "cluster[%s].node[%d]" % (cluster_id, node_number)

    # Extract management ip
    extract_management_ip = lambda node: node['management_ip']

    new_node_values = lambda node_status: (ok_status if(node_status == 'OK')
                                           else not_ok_status)
    ok_status = {'status': models.Status.ACTIVE}
    not_ok_status = {'status': models.Status.DOWN}

    flow = linear_flow.Flow(flow_name)
    flow.add(
        cue_tasks.GetNode(
            name="Get Node %s" % node_name,
            inject={'node_id': node_id},
            provides="node_%d" % node_number),
        os_common.Lambda(
            extract_management_ip,
            name="extract management ip %s" % node_name,
            rebind={'node': "node_%d" % node_number},
            provides="vm_mgmt_ip_%d" % node_number),
        cue_tasks.GetRabbitClusterStatus(
            name="get RabbitMQ cluster status_%d" % node_number,
            rebind={'vm_ip': "vm_mgmt_ip_%d" % node_number},
            provides="node_status_%d" % node_number,
            inject={'proto': 'http'}),
        os_common.Lambda(
            new_node_values,
            name="build node values %s" % node_name,
            rebind={'node_status': "node_status_%d" % node_number},
            provides="node_values_%d" % node_number),
        cue_tasks.UpdateNode(
            name="update node status %s" % node_name,
            rebind={'node_values': "node_values_%d" % node_number},
            inject={'node_id': node_id})
    )

    return flow
