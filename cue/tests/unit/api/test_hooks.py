# Copyright 2015 Hewlett-Packard Development Company, L.P.
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
# Copyright [2014] Hewlett-Packard Development Company, L.P.
# limitations under the License.
"""
Tests for API Hooks.
"""
from cue.api import hooks
from cue.tests.unit import base


class State(object):
    def __init__(self, request):
        self.request = request


class Request(object):
    def __init__(self, headers):
        self.headers = headers
        self.environ = {}
        self.context = None


class TestApiHooks(base.UnitTestCase):

    def setUp(self):
        super(TestApiHooks, self).setUp()

    def test_hooks_to_request_context_mapping(self):
        """Verify header hook values extracted for request context object."""
        headers = {
            'X-User-Id': 'test_request_user_id',
            'X-Domain-Id': 'test_request_domain_id',
            'X-Project-Id': 'test_request_project_id',
            'X-Domain-Name': 'test_request_domain_name',
            'X-Auth-Token': 'test_request_auth_token',
        }

        state = State(Request(headers=headers))
        api_hook = hooks.ContextHook(public_api_routes=None)
        api_hook.before(state=state)

        self.assertEqual(headers['X-Auth-Token'],
                         state.request.context.auth_token,
                         "Invalid Auth Token extracted from header")
        self.assertEqual(headers['X-User-Id'],
                         state.request.context.user_id,
                         "Invalid User ID extracted from header")
        self.assertEqual(headers['X-Domain-Id'],
                         state.request.context.domain_id,
                         "Invalid Domain ID extracted from header")
        self.assertEqual(headers['X-Domain-Name'],
                         state.request.context.domain_name,
                         "Invalid Domain Name extracted from header")
        self.assertEqual(headers['X-Project-Id'],
                         state.request.context.project_id,
                         "Invalid Project ID extracted from header")
        self.assertEqual(headers['X-Project-Id'],
                         state.request.context.tenant_id,
                         "Invalid Project ID extracted from header")
        self.assertEqual(headers['X-Project-Id'],
                         state.request.context.tenant,
                         "Invalid Project ID extracted from header")