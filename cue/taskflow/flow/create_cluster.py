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
import taskflow.patterns.linear_flow as linear_flow
import taskflow.retry as retry

import cue.client as client
from cue.db.sqlalchemy import models
from cue.taskflow.flow import create_cluster_node
import cue.taskflow.task as cue_tasks
import os_tasklib.common as os_common
import os_tasklib.nova as nova


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
    cluster_name = "cue[%s]" % cluster_id
    flow = graph_flow.Flow("creating cluster %s" % cluster_id)
    start_flow_cluster_update = {
        'cluster_id': cluster_id,
        'cluster_values': {'status': models.Status.BUILDING}}

    extract_scheduler_hints = lambda vm_group: {'group': str(vm_group['id'])}
    end_flow_cluster_update = lambda vm_group: {
        'status': models.Status.ACTIVE,
        'group_id': str(vm_group['id'])}

    create_cluster_start_task = cue_tasks.UpdateClusterRecord(
        name="update cluster status start %s" % cluster_name,
        inject=start_flow_cluster_update)
    flow.add(create_cluster_start_task)

    cluster_anti_affinity = cfg.CONF.taskflow.cluster_node_anti_affinity
    if cluster_anti_affinity:
        create_vm_group = nova.CreateVmGroup(
            name="create cluster group %s" % cluster_name,
            os_client=client.nova_client(),
            requires=('name', 'policies'),
            inject={'name': "cue_group_%s" % cluster_id,
                    'policies': ['anti-affinity']},
            provides="cluster_group")
        flow.add(create_vm_group)

        get_scheduler_hints = os_common.Lambda(
            extract_scheduler_hints,
            name="extract scheduler hints %s" % cluster_name,
            rebind={'vm_group': "cluster_group"},
            provides="scheduler_hints")
        flow.add(get_scheduler_hints)

        build_cluster_info = os_common.Lambda(
            end_flow_cluster_update,
            name="build new cluster update values %s" % cluster_name,
            rebind={'vm_group': "cluster_group"},
            provides="cluster_values")
        flow.add(build_cluster_info)

        flow.link(create_cluster_start_task, create_vm_group)
        flow.link(create_vm_group, get_scheduler_hints)
        flow.link(get_scheduler_hints, build_cluster_info)
        create_node_start_task = build_cluster_info
        create_cluster_end_task = cue_tasks.UpdateClusterRecord(
            name="update cluster status end %s" % cluster_name,
            inject={'cluster_id': cluster_id})
    else:
        create_node_start_task = create_cluster_start_task
        end_flow_cluster_update = {
            'cluster_id': cluster_id,
            'cluster_values': {'status': models.Status.ACTIVE}}
        create_cluster_end_task = cue_tasks.UpdateClusterRecord(
            name="update cluster status end %s" % cluster_name,
            inject=end_flow_cluster_update)

    flow.add(create_cluster_end_task)

    node_check_timeout = cfg.CONF.taskflow.cluster_node_check_timeout
    node_check_max_count = cfg.CONF.taskflow.cluster_node_check_max_count

    check_rabbit_online = linear_flow.Flow(
        name="wait for RabbitMQ ready state %s" % cluster_name,
        retry=retry.Times(node_check_max_count, revert_all=True))
    check_rabbit_online.add(
        cue_tasks.GetRabbitClusterStatus(
            name="get RabbitMQ status %s" % cluster_name,
            rebind={'vm_ip': "vm_management_ip_0"},
            provides="clustering_status",
            inject={'proto': 'http'}),
        os_common.CheckFor(
            name="check cluster status %s" % cluster_name,
            details="waiting for RabbitMQ clustered status",
            rebind={'check_var': "clustering_status"},
            check_value='OK',
            retry_delay_seconds=node_check_timeout),
    )
    flow.add(check_rabbit_online)

    flow.link(check_rabbit_online, create_cluster_end_task)

    #todo(dagnello): verify node_ids is a list and not a string
    for i, node_id in enumerate(node_ids):
        generate_userdata = cue_tasks.ClusterNodeUserData(
            name="generate userdata %s_%d" % (cluster_name, i),
            node_count=len(node_ids),
            node_ip_prefix="vm_management_ip_",
            inject={'node_name': "rabbit-node-%d" % i,
                    'cluster_id': cluster_id})
        flow.add(generate_userdata)

        create_cluster_node.create_cluster_node(
            cluster_id=cluster_id, node_number=i, node_id=node_id,
            graph_flow=flow, generate_userdata=generate_userdata,
            start_task=create_node_start_task, post_task=check_rabbit_online,
            user_network_id=user_network_id,
            management_network_id=management_network_id)
    return flow
