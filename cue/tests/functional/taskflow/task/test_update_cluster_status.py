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


from cue import client
from cue.db.sqlalchemy import models
from cue import objects
import cue.taskflow.task.update_cluster_record_task as update_cluster_status
from cue.tests.functional import base
from cue.tests.functional.fixtures import neutron
import os_tasklib.neutron as neutron_task

from neutronclient.common import exceptions
from oslo_utils import uuidutils
from taskflow import engines
from taskflow.patterns import linear_flow


class UpdateClusterRecordTest(base.FunctionalTestCase):

    additional_fixtures = [
        neutron.NeutronClient
    ]

    task_store = {
        "context": "context",
        "cluster_id": "id",
        "network_id": uuidutils.generate_uuid(),
        "port_name": "port_0",
    }

    def setUp(self):
        super(UpdateClusterRecordTest, self).setUp()

    def test_update_cluster_status(self):
        """Verifies UpdateClusterRecord task directly."""

        # setup a test cluster in DB for this test
        cluster_values = {
            "project_id": self.context.tenant_id,
            "name": "RabbitCluster",
            "network_id": uuidutils.generate_uuid(),
            "flavor": "1",
            "size": 3,
        }

        new_cluster = objects.Cluster(**cluster_values)
        new_cluster.create(self.context)

        # verify new cluster is in BUILDING state
        self.assertEqual(models.Status.BUILDING, new_cluster.status,
                         "Invalid status")

        # setup require task input variables for "UpdateClusterRecord" task
        UpdateClusterRecordTest.task_store['context'] = self.context.to_dict()
        UpdateClusterRecordTest.task_store['cluster_id'] = new_cluster.id

        # create flow with "UpdateClusterRecord" task
        self.flow = linear_flow.Flow(name="update cluster status").add(
            update_cluster_status.UpdateClusterRecord(
                name="get RabbitMQ status",
                inject={'cluster_values': {'status': models.Status.ACTIVE}}))

        # start engine to run task
        engines.run(self.flow, store=UpdateClusterRecordTest.task_store)

        # verify cluster status is now in ACTIVE state
        cluster_after = objects.Cluster.get_cluster_by_id(self.context,
                                                          new_cluster.id)
        self.assertEqual(models.Status.ACTIVE, cluster_after.status,
                         "Invalid status")

    def test_update_cluster_status_fail(self):
        """Verifies UpdateClusterRecord task failed flow scenario.

        This test simulates a failed flow with UpdateClusterRecord task
        followed by CreatePort task.  The CreateFlow task will be configured to
        fail which will in-turn fail the overall flow.  The failed flow will
        trigger UpdateClusterRecord task's revert method which will set Cluster
        status to ERROR state.
        """

        # retrieve neutron client API class
        neutron_client = client.neutron_client()

        # setup a test cluster in DB for this test
        cluster_values = {
            "project_id": self.context.tenant_id,
            "name": "RabbitCluster",
            "network_id": uuidutils.generate_uuid(),
            "flavor": "1",
            "size": 3,
        }

        new_cluster = objects.Cluster(**cluster_values)
        new_cluster.create(self.context)

        # verify new cluster is in BUILDING state
        self.assertEqual(models.Status.BUILDING, new_cluster.status,
                         "Invalid status")

        # setup require task input variables for "UpdateClusterRecord" task
        UpdateClusterRecordTest.task_store['context'] = self.context.to_dict()
        UpdateClusterRecordTest.task_store['cluster_id'] = new_cluster.id

        # create flow with "UpdateClusterRecord" task
        self.flow = linear_flow.Flow(name="update cluster status").add(
            update_cluster_status.UpdateClusterRecord(
                name="get RabbitMQ status",
                inject={'cluster_values': {'status': models.Status.BUILDING}}),
            neutron_task.CreatePort(os_client=neutron_client,
                                    provides='neutron_port_id'))

        # start engine to run task
        self.assertRaises(exceptions.NetworkNotFoundClient, engines.run,
                          self.flow, store=UpdateClusterRecordTest.task_store)

        # verify cluster status is now in ERROR state
        cluster_after = objects.Cluster.get_cluster_by_id(self.context,
                                                          new_cluster.id)
        self.assertEqual(models.Status.ERROR, cluster_after.status,
                         "Invalid status")
