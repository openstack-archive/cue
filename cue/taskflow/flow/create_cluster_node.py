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
import taskflow.retry as retry

import cue.client as client
from cue.db.sqlalchemy import models
import cue.taskflow.task as cue_tasks
import os_tasklib.common as os_common
import os_tasklib.neutron as neutron
import os_tasklib.nova as nova


def create_cluster_node(cluster_id, node_number, node_id,
                        graph_flow, generate_userdata,
                        start_task, end_task):
    """Create Cluster Node factory function

    This factory function creates a flow for creating a node of a cluster.

    :param cluster_id: Unique ID for the cluster that the node is part of.
    :type cluster_id: string
    :param node_number: Cluster node # for the node being created.
    :type node_number: number
    :param node_id: Unique ID for the node.
    :type node_id: string
    :return: A flow instance that represents the workflow for creating a
             cluster node.
    """
    node_name = "cluster[%s].node[%d]" % (cluster_id, node_number)

    extract_port_info = (lambda port_info:
                         ([{'port-id': port_info['port']['id']}],
                         port_info['port']['fixed_ips'][0]['ip_address']))

    extract_vm_id = lambda vm_info: str(vm_info['id'])

    new_node_values = lambda nova_vm_id: {'status': models.Status.ACTIVE,
                                          'instance_id': nova_vm_id}

    new_endpoint_values = lambda vm_ip: {'node_id': node_id,
                                         'uri': vm_ip + ':',
                                         'type': 'AMQP'}

    create_port =  neutron.CreatePort(
        name="create port %s" % node_name,
        os_client=client.neutron_client(),
        inject={'port_name': node_name},
        provides="port_info_%d" % node_number)
    graph_flow.add(create_port)
    graph_flow.link(start_task, create_port)

    extract_port_data = os_common.Lambda(
        extract_port_info,
        name="extract port id %s" % node_name,
        rebind={'port_info': "port_info_%d" % node_number},
        provides=("port_id_%d" % node_number, "vm_ip_%d" % node_number))
    graph_flow.add(extract_port_data)
    graph_flow.link(create_port, extract_port_data)

    graph_flow.link(extract_port_data, generate_userdata)

    create_vm = nova.CreateVm( name="create vm %s" % node_name,
        os_client=client.nova_client(),
        requires=('name', 'image', 'flavor', 'nics'),
        inject={'name': node_name},
        rebind={'nics': "port_id_%d" % node_number},
        provides="vm_info_%d" % node_number)
    graph_flow.add(create_vm)
    graph_flow.link(generate_userdata, create_vm)

    get_vm_id = os_common.Lambda( extract_vm_id,
        name="extract vm id %s" % node_name,
        rebind={'vm_info': "vm_info_%d" % node_number},
        provides="vm_id_%d" % node_number)
    graph_flow.add(get_vm_id)
    graph_flow.link(create_vm, get_vm_id)

    #todo(dagnello): make retry times configurable
    check_vm_active = linear_flow.Flow(
        name="wait for VM active state %s" % node_name,
        retry=retry.Times(12))
    check_vm_active.add(
        nova.GetVmStatus(
            os_client=client.nova_client(),
            name="get vm %s" % node_name,
            rebind={'nova_vm_id': "vm_id_%d" % node_number},
            provides="vm_status_%d" % node_number),
        os_common.CheckFor(
            name="check vm status %s" % node_name,
            rebind={'check_var': "vm_status_%d" % node_number},
            check_value='ACTIVE',
            retry_delay_seconds=10),
        )
    graph_flow.add(check_vm_active)
    graph_flow.link(get_vm_id, check_vm_active)

    #todo(dagnello): make retry times configurable
    check_rabbit_online = linear_flow.Flow(
        name="wait for RabbitMQ ready state %s" % node_name,
        retry=retry.Times(30))
    check_rabbit_online.add(
        os_common.VerifyNetwork(
            name="get RabbitMQ status %s" % node_name,
            rebind={'vm_ip': "vm_ip_%d" % node_number},
            retry_delay_seconds=10))
    graph_flow.add(check_rabbit_online)
    graph_flow.link(check_vm_active, check_rabbit_online)

    build_node_info = os_common.Lambda(
        new_node_values,
        name="build new node values %s" % node_name,
        rebind={'nova_vm_id': "vm_id_%d" % node_number},
        provides="node_values_%d" % node_number
    )
    graph_flow.add(build_node_info)
    graph_flow.link(check_rabbit_online, build_node_info)

    update_node = cue_tasks.UpdateNode(
        name="update node %s" % node_name,
        rebind={'node_values': "node_values_%d" % node_number},
        inject={'node_id': node_id})
    graph_flow.add(update_node)
    graph_flow.link(build_node_info, update_node)

    build_endpoint_info = os_common.Lambda(
        new_endpoint_values,
        name="build new endpoint values %s" % node_name,
        rebind={'vm_ip': "vm_ip_%d" % node_number},
        inject={'node_id': node_id},
        provides="endpoint_values_%d" % node_number
    )
    graph_flow.add(build_endpoint_info)
    graph_flow.link(check_rabbit_online, build_endpoint_info)

    create_endpoint = cue_tasks.CreateEndpoint(
        name="update endpoint for node %s" % node_name,
        rebind={'endpoint_values': "endpoint_values_%d" % node_number})
    graph_flow.add(create_endpoint)
    graph_flow.link(check_rabbit_online, create_endpoint)

    graph_flow.link(update_node, end_task)
    graph_flow.link(create_endpoint, end_task)
