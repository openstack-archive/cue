# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
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
from oslo_config import cfg
from oslo_config import fixture as config_fixture

from cue.cmd import api
from cue.tests.functional import base


class TestCmdApi(base.FunctionalTestCase):
    def setUp(self):
        super(TestCmdApi, self).setUp()

        # setup config fixture
        self.CONF = config_fixture.Config()
        self.useFixture(self.CONF)
        config_file_opt = cfg.StrOpt('config_file',
                                     default='')
        self.CONF.register_opt(config_file_opt)

    @mock.patch('cue.api.app.setup_app')
    @mock.patch('cue.common.service.prepare_service')
    @mock.patch('wsgiref.simple_server.make_server')
    def test_api_cmd(self, mock_wsgi, mock_prep_service, mock_setup_app):
        api.main()
        self.assertTrue(mock_wsgi.called)
        self.assertTrue(mock_prep_service.called)
        self.assertTrue(mock_setup_app.called)
