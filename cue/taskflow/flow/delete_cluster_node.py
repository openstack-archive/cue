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

import cue.client as client
from cue.db.sqlalchemy import models
import cue.taskflow.task as cue_tasks
import os_tasklib.common as os_common
import os_tasklib.neutron as neutron
import os_tasklib.nova as nova


def delete_cluster_node(cluster_id, node_number, node_id):
    """Delete Cluster Node factory function

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
    flow_name = "delete cluster %s node %d" % (cluster_id, node_number)
    node_name = "cluster[%s].node[%d]" % (cluster_id, node_number)

    extract_vm_id = lambda node: node['instance_id']
    extract_port_ids = lambda interfaces: [i['port_id'] for i in interfaces]

    deleted_node_values = {'status': models.Status.DELETED,
                           'deleted': True}

    deleted_endpoints_values = {'deleted': True}

    flow = linear_flow.Flow(flow_name)
    flow.add(
        cue_tasks.GetNode(
            name="Get Node %s" % node_name,
            inject={'node_id': node_id},
            provides="node_%d" % node_number),
        os_common.Lambda(
            extract_vm_id,
            name="extract vm id %s" % node_name,
            rebind={'node': "node_%d" % node_number},
            provides="vm_id_%d" % node_number),
        nova.ListVmInterfaces(
            os_client=client.nova_client(),
            name="list vm interfaces %s" % node_name,
            rebind={'server': "vm_id_%d" % node_number},
            inject={'ignore_nova_not_found_exception': True},
            provides="vm_interfaces_%d" % node_number),
        os_common.Lambda(
            extract_port_ids,
            name="extract port ids %s" % node_name,
            rebind={'interfaces': "vm_interfaces_%d" % node_number},
            provides="vm_port_list_%d" % node_number),
        nova.DeleteVm(
            os_client=client.nova_client(),
            name="delete vm %s" % node_name,
            rebind={'server': "vm_id_%d" % node_number}),
        neutron.DeletePorts(
            os_client=client.neutron_client(),
            name="delete vm %s ports" % node_name,
            rebind={'port_ids': "vm_port_list_%d" % node_number}),
        cue_tasks.UpdateNode(
            name="update node %s" % node_name,
            inject={'node_id': node_id,
                    'node_values': deleted_node_values}),
        cue_tasks.UpdateEndpoints(
            name="update endpoint for node %s" % node_name,
            inject={'node_id': node_id,
                    'endpoints_values': deleted_endpoints_values}
        ))
    return flow
