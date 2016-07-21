# -*- coding: utf-8 -*-
# Copyright 2014-2015 Hewlett-Packard Development Company, L.P.
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

import uuid

from cue.common import context
from cue.tests.unit import base


class TestContext(base.UnitTestCase):

    def test_context(self):
        original_context = {
            'auth_token': str(uuid.uuid4()),
            'user': str(uuid.uuid4()),
            'tenant': str(uuid.uuid4()),
            'domain': str(uuid.uuid4()),
            'user_domain': str(uuid.uuid4()),
            'project_domain': str(uuid.uuid4()),
            'is_admin': False,
            'read_only': False,
            'show_deleted': False,
            'request_id': str(uuid.uuid4()),
            'resource_uuid': str(uuid.uuid4()),
            'roles': str(uuid.uuid4()),
            'is_public_api': False,
            'domain_id': str(uuid.uuid4()),
            'domain_name': str(uuid.uuid4())
        }

        req_context = context.RequestContext(**original_context)
        context_dict = req_context.to_dict()

        # oslo.context may add things like user_identity we don't care about.
        # just check that things we set are still set.
        for k, v in original_context.items():
            self.assertEqual(v, context_dict[k])

    def test_tenant_id(self):
        tenant_id = str(uuid.uuid4())
        req_context = context.RequestContext()
        req_context.tenant_id = tenant_id
        self.assertEqual(tenant_id, req_context.tenant_id)

    def test_user_id(self):
        user_id = str(uuid.uuid4())
        req_context = context.RequestContext()
        req_context.user_id = user_id
        self.assertEqual(user_id, req_context.user_id)
