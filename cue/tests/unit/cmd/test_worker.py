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

import mock

from cue.cmd import worker
from cue.tests.unit import base


class TestWorker(base.UnitTestCase):

    @mock.patch('cue.taskflow.service.ConductorService.start')
    @mock.patch('cue.taskflow.service.ConductorService.handle_signals')
    @mock.patch('oslo_config.cfg.CONF.log_opt_values')
    @mock.patch('cue.common.service.prepare_service')
    def test_main(self, mock_prepare, mock_conf, mock_tf_signals,
                  mock_tf_start):

        worker.main()

        self.assertEqual(mock_prepare.call_count, 1)
        self.assertEqual(mock_conf.call_count, 1)
        mock_tf_signals.assert_called_once_with()
        mock_tf_start.assert_called_once_with()
