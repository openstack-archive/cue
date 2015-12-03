# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Enterprise Development Company, L.P.
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

from cue.common import policy
from cue.tests.functional import api


class TestPolicyHarness(api.APITest):
    """Test that the API Test Policy harness is only initialized once."""

    @mock.patch('cue.common.policy.init')
    def setUp(self, mock_policy_init):
        super(TestPolicyHarness, self).setUp()
        self.mock_init = mock_policy_init

    def test_assert_init_called_once(self):
        """Assert that policy is only initialized once in the test harness."""
        self.assertEqual(1, self.mock_init.call_count)


class TestPolicyOsloConfig(api.APITest):
    """Test the policy harness initialization configuration states."""

    def test_init_with_uninitialized_config_dir(self):
        self.assertNotIn('config_dir', cfg.CONF)

        try:
            policy.init()
        except Exception as e:
            self.fail("Policy initialization failed with: " + e.message)

    def test_init_with_empty_oslo_config_dir(self):
        self.CONF.conf(args=[], project='cue')

        try:
            policy.init()
        except Exception as e:
            self.fail("Policy initialization failed with: " + e.message)
