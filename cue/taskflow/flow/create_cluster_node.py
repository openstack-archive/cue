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

from oslo_config import cfg
import taskflow.patterns.linear_flow as linear_flow
import taskflow.retry as retry

import cue.client as client
from cue.db.sqlalchemy import models
import cue.taskflow.task as cue_tasks
import os_tasklib.common as os_common
import os_tasklib.neutron as neutron
import os_tasklib.nova as nova


CONF = cfg.CONF

FLOW_OPTS = [
    cfg.IntOpt('create_cluster_node_vm_active_retry_count',
               default=12),
]

CONF.register_opts(FLOW_OPTS, group='flow_options')


def create_cluster_node(cluster_id, node_number, node_id, graph_flow,
                        generate_userdata, start_task, post_task,
                        node_check_timeout, node_check_max_count,
                        user_network_id, management_network_id):
    """Create Cluster Node factory function

    This factory function creates a flow for creating a node of a cluster.

    :param cluster_id: Unique ID for the cluster that the node is part of.
    :type cluster_id: string
    :param node_number: Cluster node # for the node being created.
    :type node_number: number
    :param node_id: Unique ID for the node.
    :type node_id: string
    :param graph_flow: TaskFlow graph flow which contains create cluster flow
    :type graph_flow: taskflow.patterns.graph_flow
    :param start_task: Update cluster status start task
    :type start_task: cue.taskflow.task.UpdateClusterStatus
    :param post_task: Task/Subflow to run after the flow created here
    :type post_task: taskflow task or flow
    :param generate_userdata: generate user data task
    :type generate_userdata: cue.taskflow.task.ClusterNodeUserData
    :param node_check_timeout: seconds wait between node status checks
    :type node_check_timeout: int
    :param node_check_max_count: times to check for updated node status
    :type node_check_max_count: int
    :param user_network_id: The user's network id
    :type user_network_id: string
    :param management_network_id: The management network id
    :type management_network_id: string
    :return: A flow instance that represents the workflow for creating a
             cluster node.
    """
    node_name = "cue[%s].node[%d]" % (cluster_id, node_number)

    extract_port_info = (lambda user_port_info, management_port_info:
                         (
                         [  # nova boot requires a list of port-id's
                            {'port-id': user_port_info['port']['id']},
                            {'port-id': management_port_info['port']['id']}
                         ],
                         # user port ip
                         user_port_info['port']['fixed_ips'][0]['ip_address'],
                         # management port ip
                         management_port_info['port']['fixed_ips'][0]
                         ['ip_address']))

    extract_vm_id = lambda vm_info: str(vm_info['id'])

    new_node_values = lambda nova_vm_id, vm_management_ip: {
                                          'status': models.Status.ACTIVE,
                                          'instance_id': nova_vm_id,
                                          'management_ip': vm_management_ip}

    new_endpoint_values = lambda vm_ip: {'node_id': node_id,
                                         'uri': vm_ip + ':',
                                         'type': 'AMQP'}

    create_user_port = neutron.CreatePort(
        name="create port %s" % node_name,
        os_client=client.neutron_client(),
        inject={'network_id': user_network_id,
                'port_name': 'user_' + node_name},
        provides="user_port_info_%d" % node_number)
    graph_flow.add(create_user_port)
    graph_flow.link(start_task, create_user_port)

    create_management_port = neutron.CreatePort(
        name="create management port %s" % node_name,
        os_client=client.neutron_client(),
        inject={'network_id': management_network_id,
                'port_name': 'management_' + node_name},
        provides="management_port_info_%d" % node_number)
    graph_flow.add(create_management_port)
    graph_flow.link(start_task, create_management_port)

    extract_port_data = os_common.Lambda(
        extract_port_info,
        name="extract port id %s" % node_name,
        rebind={'user_port_info': "user_port_info_%d" % node_number,
                'management_port_info': "management_port_info_%d" %
                                        node_number},
        provides=("port_ids_%d" % node_number,
                  "vm_user_ip_%d" % node_number,
                  "vm_management_ip_%d" % node_number))
    graph_flow.add(extract_port_data)
    graph_flow.link(create_user_port, extract_port_data)

    create_vm = nova.CreateVm(name="create vm %s" % node_name,
        os_client=client.nova_client(),
        requires=('name', 'image', 'flavor', 'nics'),
        inject={'name': node_name},
        rebind={'nics': "port_ids_%d" % node_number},
        provides="vm_info_%d" % node_number)
    graph_flow.add(create_vm)
    graph_flow.link(create_management_port, create_vm)
    graph_flow.link(generate_userdata, create_vm)

    get_vm_id = os_common.Lambda(extract_vm_id,
        name="extract vm id %s" % node_name,
        rebind={'vm_info': "vm_info_%d" % node_number},
        provides="vm_id_%d" % node_number)
    graph_flow.add(get_vm_id)
    graph_flow.link(create_vm, get_vm_id)

    retry_count = CONF.flow_options.create_cluster_node_vm_active_retry_count
    #todo(dagnello): make retry times configurable
    check_vm_active = linear_flow.Flow(
        name="wait for VM active state %s" % node_name,
        retry=retry.Times(retry_count, revert_all=True))
    check_vm_active.add(
        nova.GetVmStatus(
            os_client=client.nova_client(),
            name="get vm %s" % node_name,
            rebind={'nova_vm_id': "vm_id_%d" % node_number},
            provides="vm_status_%d" % node_number),
        os_common.CheckFor(
            name="check vm status %s" % node_name,
            details="waiting for ACTIVE VM status",
            rebind={'check_var': "vm_status_%d" % node_number},
            check_value='ACTIVE',
            retry_delay_seconds=10),
        )
    graph_flow.add(check_vm_active)
    graph_flow.link(get_vm_id, check_vm_active)

    build_node_info = os_common.Lambda(
        new_node_values,
        name="build new node values %s" % node_name,
        rebind={'nova_vm_id': "vm_id_%d" % node_number,
                'vm_management_ip': "vm_management_ip_%d" % node_number},
        provides="node_values_%d" % node_number
    )
    graph_flow.add(build_node_info)
    graph_flow.link(get_vm_id, build_node_info)

    update_node = cue_tasks.UpdateNode(
        name="update node %s" % node_name,
        rebind={'node_values': "node_values_%d" % node_number},
        inject={'node_id': node_id})
    graph_flow.add(update_node)
    graph_flow.link(build_node_info, update_node)

    build_endpoint_info = os_common.Lambda(
        new_endpoint_values,
        name="build new endpoint values %s" % node_name,
        rebind={'vm_ip': "vm_user_ip_%d" % node_number},
        inject={'node_id': node_id},
        provides="endpoint_values_%d" % node_number
    )
    graph_flow.add(build_endpoint_info)
    graph_flow.link(check_vm_active, build_endpoint_info)

    create_endpoint = cue_tasks.CreateEndpoint(
        name="update endpoint for node %s" % node_name,
        rebind={'endpoint_values': "endpoint_values_%d" % node_number})
    graph_flow.add(create_endpoint)
    graph_flow.link(check_vm_active, create_endpoint)

    graph_flow.link(update_node, post_task)
    graph_flow.link(create_endpoint, post_task)
