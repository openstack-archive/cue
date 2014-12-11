# -*- encoding: utf-8 -*-
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
"""
Tests for the API /clusters/ methods.
"""

import cue.tests.api as api_base
from cue.tests.db import utils as dbutils


# class TestClusterObject(base.TestCase):
#
#     def test_cluster_init(self):
#         # port_dict = apiutils.port_post_data(node_id=None)
#         # del port_dict['extra']
#         # port = api_port.Port(**port_dict)
#         # self.assertEqual(wtypes.Unset, port.extra)


class TestListClusters(api_base.FunctionalTest):

    cluster_name = "test-cluster"

    def setUp(self):
        super(TestListClusters, self).setUp()
        #self.cluster = dbutils.create_test_cluster()

    def test_empty(self):
        data = self.get_json('/clusters')
        # TODO(vipul): This should probably return a empty 'clusters'
        self.assertEqual([], data)

    def test_one(self):
        cluster = dbutils.create_test_cluster(name=self.cluster_name)
        data = self.get_json('/clusters')

        self.assertEqual(cluster.id, data[0]["id"])
        self.assertEqual(self.cluster_name, data[0]["name"])
