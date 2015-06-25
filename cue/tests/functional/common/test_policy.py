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

from cue.common import exception
from cue.common import policy
from cue.tests.functional import base


_test_policy_dict = {
    "admin": "role:admin or is_admin:True",
    "owner": "tenant:%(tenant_id)s",
    "admin_or_owner": "rule:admin or rule:owner",

    "default": "rule:admin_or_owner",

    "cluster:create": "rule:admin_or_owner",
    "cluster:get": "rule:admin_or_owner",
    "cluster:delete": "rule:admin_or_owner",
    "cluster:update_status": "rule:admin_or_owner",
    "clusters:get": "rule:admin_or_owner"
}

_test_policy_json = """{
    "admin": "role:admin or is_admin:True",
    "owner": "tenant:%(tenant_id)s",
    "admin_or_owner": "rule:admin or rule:owner",

    "default": "rule:admin_or_owner",

    "cluster:create": "rule:admin_or_owner",
    "cluster:get": "rule:admin_or_owner",
    "cluster:delete": "rule:admin_or_owner",
    "cluster:update_status": "rule:admin_or_owner",
    "clusters:get": "rule:admin_or_owner"
}"""


class TestPolicy(base.FunctionalTestCase):

    def setUp(self):
        super(TestPolicy, self).setUp()

        self.saved_policy_enforcer = policy._ENFORCER
        policy._ENFORCER = None

    def tearDown(self):
        policy._ENFORCER = self.saved_policy_enforcer
        super(TestPolicy, self).tearDown()

    def test_init_policy(self):
        self.assertIsNone(policy._ENFORCER)
        policy.init()
        self.assertIsNotNone(policy._ENFORCER)

    @mock.patch('oslo_config.cfg.CONF.find_file')
    def test_init_policy_from_bogus_path(self, mock_find_file):
        #setup bogus path
        self.assertIsNone(policy._ENFORCER)
        policy_default_rule_opt = cfg.StrOpt('config_dir',
                                             default='/some_bogus_path')
        self.CONF.register_opt(policy_default_rule_opt)

        self.assertRaises(exception.ConfigurationError, policy.init)
        self.assertTrue(mock_find_file.called)

    def test_reset_existing_policy(self):
        policy.init()
        self.assertIsNotNone(policy._ENFORCER)
        policy.reset()
        self.assertIsNone(policy._ENFORCER)

    def test_reset_nonexisting_policy(self):
        self.assertIsNone(policy._ENFORCER)
        policy.reset()
        self.assertIsNone(policy._ENFORCER)
