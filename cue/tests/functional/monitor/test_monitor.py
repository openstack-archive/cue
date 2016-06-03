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

import uuid

import mock
from oslo_config import cfg

from cue.db.sqlalchemy import models
from cue.monitor import monitor_service as cue_monitor_service
from cue import objects
import cue.taskflow.client as tf_client
from cue.tests.functional import base

CONF = cfg.CONF


class MonitorFunctionalTests(base.FunctionalTestCase):

    cue_monitor_service = None
    active_cluster_id = None
    error_cluster_id = None
    down_cluster_id = None

    def setUp(self):
        super(MonitorFunctionalTests, self).setUp()

        CONF.set_override("coord_url", "zake", group="taskflow",
                          enforce_type=True)
        CONF.set_override("zk_hosts", "", group="taskflow",
                          enforce_type=True)
        CONF.set_override("zk_port", "", group="taskflow",
                          enforce_type=True)

        self.active_cluster_id = uuid.uuid4()
        self.error_cluster_id = uuid.uuid4()
        self.down_cluster_id = uuid.uuid4()

        # Add some test clusters
        set_up_test_clusters(
            self.context, models.Status.ACTIVE, self.active_cluster_id, 3
        )
        set_up_test_clusters(
            self.context, models.Status.ERROR, self.error_cluster_id, 3
        )
        set_up_test_clusters(
            self.context, models.Status.DOWN, self.down_cluster_id, 1
        )

        self.cue_monitor_service = cue_monitor_service.MonitorService()

    def tearDown(self):
        self.cue_monitor_service.stop()
        super(MonitorFunctionalTests, self).tearDown()

    def test_check_lock(self):
        # Lock should not be acquired yet
        self.assertFalse(self.cue_monitor_service.lock.acquired)

        self.cue_monitor_service.check()
        # Lock should have been reacquired
        self.assertTrue(self.cue_monitor_service.lock.acquired)

    @mock.patch('tooz.drivers.zookeeper.ZooKeeperLock.acquire')
    def test_lock_unacquirable(self, mock_acquire_lock):
        self.cue_monitor_service.check()
        # Lock should not have been acquired
        self.assertFalse(self.cue_monitor_service.lock.acquired)

    def test_check(self):
        tf_instance = tf_client.get_client_instance()
        start_job_list = tf_instance.joblist()
        start_job_list_length = len(start_job_list)

        # Test while job board is empty
        self.cue_monitor_service.check()

        end_job_list = sorted(tf_instance.joblist())
        end_job_list_length = len(end_job_list)

        self.assertEqual(2, end_job_list_length - start_job_list_length,
                         "Job list should only have two "
                         "clusters: " + str(tf_instance.joblist()))

        # Test while job board has 2 entries
        self.cue_monitor_service.check()

        # No new jobs should have been added.
        new_end_job_list = sorted(tf_instance.joblist())

        self.assertEqual(end_job_list, new_end_job_list,
                         "Job list should not have changed")

    def test_get_cluster_id_node_ids(self):
        clusters = cue_monitor_service.get_cluster_id_node_ids()

        self.assertEqual(2, len(clusters),
                         "Expected to find two clusters.  Only the ACTIVE"
                         " and DOWN clusters.  Found: " + str(len(clusters)))

        for cluster in clusters:
            if cluster[0] == str(self.active_cluster_id):
                self.assertEqual(3, len(cluster[1]),
                                 "Expected to find three nodes in this "
                                 "cluster.  Found: " + str(cluster[1]))
            elif cluster[0] == str(self.down_cluster_id):
                self.assertEqual(1, len(cluster[1]),
                                 "Expected to find one node in this "
                                 "cluster.  Found: " + str(cluster[1]))
            else:
                self.assertEqual(0, 1,
                                 "The only clusters returned should have been"
                                 " those created by this test.  Found a "
                                 "cluster id that does not match: " + str(
                                     cluster[0]))


def set_up_test_clusters(context, status, cluster_id, size):

    cluster_values = {
        "id": cluster_id,
        "project_id": "test_project_id",
        "name": "test_cluster",
        "network_id": "test_uuid",
        "flavor": "1",
        "size": size,
    }
    new_cluster = objects.Cluster(**cluster_values)
    new_cluster.create(context)

    new_cluster.status = status
    new_cluster.update(context, cluster_id)
