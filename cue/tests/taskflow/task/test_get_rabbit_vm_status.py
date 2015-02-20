# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import uuid

from cue.db.sqlalchemy import models
from cue import objects
import cue.taskflow.task.get_rabbit_vm_status as get_rabbit_vm_status
from cue.tests import base
from cue.tests.test_fixtures import telnet

from taskflow import engines
from taskflow.patterns import linear_flow
import taskflow.retry as retry

SHARED_CONF = {
    'connection': 'zookeeper',
}


class GetRabbitVmStatusTest(base.TestCase):
    additional_fixtures = [
        telnet.TelnetClient
    ]

    task_store = {
        'vm_ip': "0.0.0.0",
        'rabbit_port': '5672'
    }

    def setUp(self):
        super(GetRabbitVmStatusTest, self).setUp()

    def test_get_rabbit_status(self):
        """Verifies GetRabbitVmStatus task directly."""

        # setup a test cluster/nodes for this test
        cluster_values = {
            "project_id": self.context.tenant_id,
            "name": "RabbitCluster",
            "network_id": uuid.uuid4(),
            "flavor": "1",
            "size": 3,
        }

        new_cluster = objects.Cluster(**cluster_values)
        new_cluster.create(self.context)

        nodes = objects.Node.get_nodes_by_cluster_id(self.context,
                                                     new_cluster.id)

        node_before = nodes.pop()

        self.assertEqual(models.Status.BUILDING, node_before.status,
                         "Invalid status")

        # create flow with "GetRabbitVmStatus" task
        self.flow = linear_flow.Flow(name="wait for RabbitMQ ready state",
                         retry=retry.Times(1)).add(
            get_rabbit_vm_status.GetRabbitVmStatus(
                name="get RabbitMQ status",
                inject={'node_id': node_before.id,
                        'context': self.context.to_dict()},
                provides="rabbit_status",
                retry_delay_seconds=1),
        )

        # start engine to run task
        engines.run(self.flow, store=GetRabbitVmStatusTest.task_store)

        # verify node status is now in Active state
        node_after = objects.Node.get_node_by_id(self.context, node_before.id)
        self.assertEqual(models.Status.ACTIVE, node_after.status,
                         "Invalid status")

    def test_get_vm_status_flow(self):
        """Verifies GetRabbitVmStatus in a successful retry flow

        This test simulates creating a cluster, then directly running a flow
        which will fail until telnet_status acquired from get_rabbit_vm_status
        task returns 'connect'.  Attempting the telnet connection will return
        'wait' for the first three times, then will return 'connected' once a
        telnet connection is made.  The node status should be in Active state.
        """
        # configure custom vm_status list
        telnet.TelnetStatusDetails.set_telnet_status(['connected',
                                                      'wait',
                                                      'wait',
                                                      'wait'])

        # setup a test cluster/nodes for this test
        cluster_values = {
            "project_id": self.context.tenant_id,
            "name": "RabbitCluster",
            "network_id": uuid.uuid4(),
            "flavor": "1",
            "size": 1,
        }

        new_cluster = objects.Cluster(**cluster_values)
        new_cluster.create(self.context)

        nodes = objects.Node.get_nodes_by_cluster_id(self.context,
                                                     new_cluster.id)

        node_before = nodes.pop()

        self.assertEqual(models.Status.BUILDING, node_before.status,
                         "Invalid status")

        # create flow with "GetRabbitVmStatus" task
        self.flow = linear_flow.Flow(name="wait for RabbitMQ ready state",
                         retry=retry.Times(5)).add(
            get_rabbit_vm_status.GetRabbitVmStatus(
                name="get RabbitMQ status",
                inject={'node_id': node_before.id,
                        'context': self.context.to_dict()},
                provides="rabbit_status",
                retry_delay_seconds=1))

        # start engine to run task
        engines.run(self.flow, store=GetRabbitVmStatusTest.task_store)

        # verify node status is now in Active state
        node_after = objects.Node.get_node_by_id(self.context, node_before.id)
        self.assertEqual(models.Status.ACTIVE, node_after.status,
                         "Invalid status")

    def test_get_vm_status_flow_fail(self):
        """Verifies GetRabbitVmStatus in an unsuccessful retry flow

        This test simulates creating a cluster, then directly running a flow
        which will fail until the retry count has been exhausted.  Attempting
        the telnet connection will return 'wait' until retry count reaches
        limit and flow fails.  The node status should remain in Building state.
        """
        # configure custom vm_status list
        telnet.TelnetStatusDetails.set_telnet_status(['wait',
                                                      'wait',
                                                      'wait',
                                                      'wait'])

        # setup a test cluster/nodes for this test
        cluster_values = {
            "project_id": self.context.tenant_id,
            "name": "RabbitCluster",
            "network_id": uuid.uuid4(),
            "flavor": "1",
            "size": 1,
        }

        new_cluster = objects.Cluster(**cluster_values)
        new_cluster.create(self.context)

        nodes = objects.Node.get_nodes_by_cluster_id(self.context,
                                                     new_cluster.id)

        node_before = nodes.pop()

        self.assertEqual(models.Status.BUILDING, node_before.status,
                         "Invalid status")

        # create flow with "GetRabbitVmStatus" task
        self.flow = linear_flow.Flow(name="wait for RabbitMQ ready state",
                         retry=retry.Times(3)).add(
            get_rabbit_vm_status.GetRabbitVmStatus(
                name="get RabbitMQ status",
                inject={'node_id': node_before.id,
                        'context': self.context.to_dict()},
                provides="rabbit_status",
                retry_delay_seconds=1),
        )

        # start engine to run task
        self.assertRaises(IOError, engines.run, self.flow,
                          store=GetRabbitVmStatusTest.task_store)

        # verify node status is still in Building state
        node_after = objects.Node.get_node_by_id(self.context, node_before.id)
        self.assertEqual(models.Status.BUILDING, node_after.status,
                         "Invalid status")