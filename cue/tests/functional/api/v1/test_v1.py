# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
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

from cue.tests.functional import api


class TestV1Controller(api.APITest):

    def test_get_v1_root(self):
        """test case for get in v1 controller."""
        data = self.get_json('/v1')
        self.assertEqual('v1', data['id'])
        # Check fields are not empty
        for f in data.keys():
            self.assertNotIn(f, ['', []])

        # Check if all known resources are present and there are no extra ones.
        not_resources = ('id', 'status')
        actual_resource = list(set(data.keys()) - set(not_resources))
        expected_resource = ['clusters']
        self.assertEqual(expected_resource, actual_resource)
