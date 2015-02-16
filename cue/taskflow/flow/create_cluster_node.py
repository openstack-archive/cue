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
import os_tasklib.common as os_common
import os_tasklib.neutron as neutron
import os_tasklib.nova as nova


def create_cluster_node(cluster_id, node_number):
    flow_name = "create cluster %s node %d" % (cluster_id, node_number)
    node_name = "cluster[%s].node[%d]" % (cluster_id, node_number)

    extract_port_id = (lambda port_info:
                       [{'port-id': port_info['port']['id']}])

    extract_vm_id = lambda vm_info: vm_info['id']

    extract_vm_status = lambda vm_info: vm_info['status']

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
        linear_flow.Flow(name="wait for active state %s" % node_name,
                         retry=retry.Times(12)).add(
            nova.GetVm(
                os_client=client.nova_client(),
                name="get vm %s" % node_name,
                rebind={'server': "vm_id_%d" % node_number},
                provides="vm_info_%d" % node_number),
            os_common.Lambda(
                extract_vm_status,
                name="extract vm status %s" % node_name,
                rebind={'vm_info': "vm_info_%d" % node_number},
                provides="vm_status_%d" % node_number),
            os_common.CheckFor(
                name="check vm status %s" % node_name,
                rebind={'check_var': "vm_status_%d" % node_number},
                check_value='ACTIVE',
                timeout_seconds=10),
            ),
        )
    return flow
