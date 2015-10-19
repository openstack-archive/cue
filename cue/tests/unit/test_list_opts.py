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


import cue as cue
import cue.api as cue_api
import cue.api.app as cue_api_app
import cue.cmd.worker as cue_cmd_worker
import cue.common.service as cue_common_service
import cue.monitor as cue_monitor
import cue.taskflow as cue_taskflow
from cue.tests.unit import base


class OsloConfigGenTestCase(base.UnitTestCase):
    def setUp(self):
        super(OsloConfigGenTestCase, self).setUp()

    def tearDown(self):
        super(OsloConfigGenTestCase, self).tearDown()

    def test_global_opts(self):
        opts = cue.list_opts()
        self.assertEqual(1, len(opts))
        self.assertEqual('DEFAULT', opts[0][0])

    def test_api_opts(self):
        opts = cue_api.list_opts()
        self.assertEqual(1, len(opts))
        self.assertEqual('api', opts[0][0])

    def test_api_app_opts(self):
        opts = cue_api_app.list_opts()
        self.assertEqual(2, len(opts))
        self.assertEqual('DEFAULT', opts[0][0])
        self.assertEqual('api', opts[1][0])

    def test_cmd_worker_opts(self):
        opts = cue_cmd_worker.list_opts()
        self.assertEqual(1, len(opts))
        self.assertEqual('worker', opts[0][0])

    def test_common_service_opts(self):
        opts = cue_common_service.list_opts()
        self.assertEqual(1, len(opts))
        self.assertEqual('DEFAULT', opts[0][0])

    def test_monitor_opts(self):
        opts = cue_monitor.list_opts()
        self.assertEqual(1, len(opts))
        self.assertEqual('cue_monitor', opts[0][0])

    def test_taskflow_opts(self):
        opts = cue_taskflow.list_opts()
        self.assertEqual(1, len(opts))
        self.assertEqual('taskflow', opts[0][0])
