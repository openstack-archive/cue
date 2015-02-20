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
import cue.taskflow.task as cue_tasks
import os_tasklib.common as os_common
import os_tasklib.neutron as neutron
import os_tasklib.nova as nova


def create_cluster_node(context, cluster_id, node_number, node_id):
    """Create Cluster Node factory function

    This factory function creates a flow for creating a node of a cluster.

    :param cluster_id: Unique ID for the cluster that the node is part of.
    :type cluster_id: string
    :param node_number: Cluster node # for the node being created.
    :type node_number: number
    :return: A flow instance that represents the workflow for creating a
             cluster node.
    """
    flow_name = "create cluster %s node %d" % (cluster_id, node_number)
    node_name = "cluster[%s].node[%d]" % (cluster_id, node_number)

    extract_port_id = (lambda port_info:
                       [{'port-id': port_info['port']['id']}])

    extract_port_ip = (lambda port_info:
                       port_info['port']['fixed_ips'][0]['ip_address'])

    extract_vm_id = lambda vm_info: vm_info['id']

    flow = linear_flow.Flow(flow_name)
    flow.add(
        neutron.CreatePort(
            name="create port %s" % node_name,
            os_client=client.neutron_client(),
            inject={'port_name': node_name},
            provides="port_info_%d" % node_number),
        os_common.Lambda(
            extract_port_id,
            name="extract port id %s" % node_name,
            rebind={'port_info': "port_info_%d" % node_number},
            provides="port_id_%d" % node_number),
        os_common.Lambda(
            extract_port_ip,
            name="extract port ip %s" % node_name,
            rebind={'port_info': "port_info_%d" % node_number},
            provides="vm_ip_%d" % node_number),
        nova.CreateVm(
            name="create vm %s" % node_name,
            os_client=client.nova_client(),
            requires=('name', 'image', 'flavor', 'nics'),
            inject={'name': node_name},
            rebind={'nics': "port_id_%d" % node_number},
            provides="vm_info_%d" % node_number),
        os_common.Lambda(
            extract_vm_id,
            name="extract vm id %s" % node_name,
            rebind={'vm_info': "vm_info_%d" % node_number},
            provides="vm_id_%d" % node_number),
        linear_flow.Flow(name="wait for VM active state %s" % node_name,
                         retry=retry.Times(12)).add(
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
            ),
        linear_flow.Flow(name="wait for RabbitMQ ready state %s" % node_name,
                         retry=retry.Times(10)).add(
            cue_tasks.GetRabbitVmStatus(
                name="get RabbitMQ status %s" % node_name,
                inject={'node_id': node_id, 'context': context},
                rebind={'vm_ip': "vm_ip_%d" % node_number},
                provides="rabbit_status_%d" % node_number,
                retry_delay_seconds=10),
            )
        )
    return flow
