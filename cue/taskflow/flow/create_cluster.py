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

import oslo_config.cfg as cfg
import taskflow.patterns.graph_flow as graph_flow

from cue.db.sqlalchemy import models
from cue.taskflow.flow import create_cluster_node
import cue.taskflow.task as cue_tasks


def create_cluster(cluster_id, node_ids, user_network_id,
                   management_network_id):
    """Create Cluster flow factory function

    This factory function uses :func:`cue.taskflow.flow.create_cluster_node` to
    create a multi node cluster.

    :param cluster_id: A unique ID assigned to the cluster being created
    :type cluster_id: string
    :param node_ids: The Cue Node id's associated with each node in the cluster
    :type node_ids: list of uuid strings
    :param user_network_id: The user's network id
    :type user_network_id: string
    :param management_network_id: The management network id
    :type management_network_id: string
    :return: A flow instance that represents the workflow for creating a
             cluster
    """
    flow = graph_flow.Flow("creating cluster %s" % cluster_id)
    start_flow_status = {'cluster_id': cluster_id,
                         'cluster_values': {'status': models.Status.BUILDING}}
    end_flow_status = {'cluster_id': cluster_id,
                       'cluster_values': {'status': models.Status.ACTIVE}}

    start_task = cue_tasks.UpdateClusterStatus(
        name="update cluster status start "
             "%s" % cluster_id,
        inject=start_flow_status)
    flow.add(start_task)

    end_task = cue_tasks.UpdateClusterStatus(
        name="update cluster status end "
             "%s" % cluster_id,
        inject=end_flow_status)
    flow.add(end_task)

    node_check_timeout = cfg.CONF.taskflow.cluster_node_check_timeout
    node_check_max_count = cfg.CONF.taskflow.cluster_node_check_max_count

    #todo(dagnello): verify node_ids is a list and not a string
    for i, node_id in enumerate(node_ids):
        generate_userdata = cue_tasks.ClusterNodeUserData(
            "userdata_%d" % i,
            len(node_ids),
            "vm_management_ip_",
            inject={'node_name': "rabbit-node-%d" % i})
        flow.add(generate_userdata)

        create_cluster_node.create_cluster_node(cluster_id, i, node_id, flow,
                                                generate_userdata, start_task,
                                                end_task, node_check_timeout,
                                                node_check_max_count,
                                                user_network_id,
                                                management_network_id)

    return flow
