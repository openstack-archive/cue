# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Authors: Daniel Allegood <daniel.allegood@hpe.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Copyright [2015] Hewlett-Packard Development Company, L.P.
# limitations under the License.


import mock
from oslo_config import cfg
from oslotest import base as oslo_base

from cue.monitor import monitor_service as cue_monitor_service

CONF = cfg.CONF


class TestMonitorService(oslo_base.BaseTestCase):

    cue_monitor_service = None

    @mock.patch('tooz.coordination.get_coordinator')
    def setUp(self, mock_tooz_coordinator):
        super(TestMonitorService, self).setUp()
        CONF.set_override("zk_hosts", "test_host", group="taskflow")
        CONF.set_override("zk_port", "test_port", group="taskflow")

        self.cue_monitor_service = cue_monitor_service.MonitorService()

    @mock.patch('oslo_service.loopingcall.LoopingCallBase.wait')
    @mock.patch('oslo_service.loopingcall.FixedIntervalLoopingCall.start')
    def test_start(self,
                   mock_fixed_interval_loop_call_start,
                   mock_loop_call_wait):
        CONF.set_override("loop_interval_seconds", "9001",
                          group="cue_monitor")

        self.cue_monitor_service.start()

        mock_fixed_interval_loop_call_start.assert_called_once_with(
            interval=9001)
        mock_loop_call_wait.assert_called_once_with()

    def test_stop(self):
        self.cue_monitor_service.stop()

        lock_calls = map(
            lambda call: call[0],
            self.cue_monitor_service.lock.method_calls
        )
        self.assertIn("release", lock_calls)

        coordinator_calls = map(
            lambda call: call[0],
            self.cue_monitor_service.coordinator.method_calls
        )
        self.assertIn("stop", coordinator_calls)

    def test_wait(self):
        pass

    def test_reset(self):
        self.cue_monitor_service.stop()

        lock_calls = map(
            lambda call: call[0],
            self.cue_monitor_service.lock.method_calls
        )
        self.assertIn("release", lock_calls)

        coordinator_calls = map(
            lambda call: call[0],
            self.cue_monitor_service.coordinator.method_calls
        )
        self.assertIn("stop", coordinator_calls)

    @mock.patch('cue.taskflow.client.get_client_instance')
    @mock.patch('cue.monitor.monitor_service.get_cluster_id_node_ids')
    def test_check(self,
                   mock_get_cluster_id_node_ids,
                   mock_get_tf_client):
        self.cue_monitor_service.check()

        mock_get_cluster_id_node_ids.assert_called_once_with()
        mock_get_tf_client.assert_called_once_with()

        # Get all mock calls to the taskflow_client magicMock object
        tf_calls = map(
            lambda call: call[0],
            mock_get_tf_client.mock_calls
        )
        # Filter for any call containing "joblist"
        tf_joblist_called = filter(lambda mock_call:
                                   "joblist" in mock_call,
                                   tf_calls)
        self.assertIsNot(0, len(tf_joblist_called))

    @mock.patch('cue.db.api.Connection.get_clusters')
    @mock.patch('cue.db.api.get_instance')
    def test_get_cluster_id_node_ids(self,
                                     mock_get_db_instance,
                                     mock_get_clusters):
        cue_monitor_service.get_cluster_id_node_ids()

        mock_get_db_instance.assert_called_once_with()

        # Get all mock calls to the taskflow_client magicMock object
        db_api_calls = map(
            lambda call: {"name": call[0],
                          "positional_args": call[1],
                          "explicit_args": call[2]
                          },
            mock_get_db_instance.mock_calls
        )

        # Filter for any call containing "joblist"
        db_api_get_clusters_called = filter(
            lambda mock_call:
            check_mock_calls_for_args(mock_call),
            db_api_calls)

        self.assertIsNot(0, len(db_api_get_clusters_called))


def check_mock_calls_for_args(mock_call):
    return (
        "get_clusters" in mock_call['name'] and
        None in mock_call['positional_args'] and
        'project_only' in mock_call['explicit_args'] and
        mock_call['explicit_args']['project_only'] == False)
