# -*- encoding: utf-8 -*-
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

from oslo_config import cfg
from oslo_config import fixture as config_fixture

from cue.common import service
from cue.tests.unit import base


class TestCommonService(base.UnitTestCase):

    def setUp(self):

        super(TestCommonService, self).setUp()

        # setup config fixture
        self.CONF = config_fixture.Config()
        self.useFixture(self.CONF)

    def test_prepare_service(self):
        service.prepare_service(['cue-api',
                                 '--config-file',
                                 'etc/cue/cue.conf.sample'])
        self.assertEqual('cue', cfg.CONF.project)
