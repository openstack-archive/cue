# Copyright 2014 OpenStack Foundation
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

import logging

import tempest_lib.base
from tempest_lib.common.utils import data_utils

from integrationtests.api.v1.clients import clusters_client


LOG = logging.getLogger(__name__)


class ClusterTest(tempest_lib.base.BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super(ClusterTest, cls).setUpClass()
        cls.client = clusters_client.MessageQueueClustersClient()

    def setUp(self):
        super(ClusterTest, self).setUp()
        self.cluster = self.create_cluster()

    def tearDown(self):
        super(ClusterTest, self).tearDown()
        self.client.delete_cluster(self.cluster['id'])

    @classmethod
    def create_cluster(cls):
        name = data_utils.rand_name(ClusterTest.__name__ + "-cluster")
        network_id = [cls.client.private_network['id']]
        flavor = '8795'
        return cls.client.create_cluster(name, flavor, network_id)

    def test_list_clusters(self):
        clusters = self.client.list_clusters()
        self.assertIn('id', clusters.data)
        self.assertIn('status', clusters.data)

    def test_get_cluster(self):
        cluster_resp = self.client.get_cluster_details(self.cluster['id'])
        self.assertEqual(self.cluster['id'], cluster_resp['id'])
        self.assertEqual(self.cluster['name'], cluster_resp['name'])
