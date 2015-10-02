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

from cue.cmd import monitor
from cue.tests.unit import base


class TestMonitor(base.UnitTestCase):

    @mock.patch('tooz.coordination.get_coordinator')
    @mock.patch('oslo_service.service.ServiceLauncher.wait')
    @mock.patch('oslo_config.cfg.CONF.log_opt_values')
    @mock.patch('cue.common.service.prepare_service')
    def test_main(self,
                  mock_prepare,
                  mock_conf,
                  mock_oslo_service_wait,
                  mock_tooz_get_coordinator):

        monitor.main()

        mock_tooz_get_coordinator.assert_called_once_with(
            'zookeeper://localhost:2181', 'cue-monitor')
        mock_oslo_service_wait.assert_called_once_with()
        self.assertEqual(mock_conf.call_count, 1)
        self.assertEqual(mock_prepare.call_count, 1)
