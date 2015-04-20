# Copyright 2014, Hewlett-Packard
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock
from oslo.config import cfg

from cue.common import service
from cue.tests.unit import base


class TestCommonService(base.UnitTestCase):

    def test_prepare_service(self):
        service.prepare_service([])
        self.assertEqual('cue', cfg.CONF.project)

    @mock.patch('sys.argv')
    def test_prepare_service_noargs(self, mock_sys):
        service.prepare_service()
        self.assertEqual('cue', cfg.CONF.project)
