# Copyright 2015 OpenStack Foundation
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

"""
Tests for the API /cluster/ controller methods.
"""

import logging

import tempest_lib.base
from tempest_lib.common.utils import data_utils
from tempest_lib import exceptions as tempest_exceptions

from tests.integration.api.v1.clients import clusters_client
from tests.integration.common import config


CONF = config.get_config()
LOG = logging.getLogger(__name__)


class ClusterTest(tempest_lib.base.BaseTestCase):
    """Cluster integration tests for Cue."""

    @classmethod
    def setUpClass(cls):
        super(ClusterTest, cls).setUpClass()
        cls.client = clusters_client.MessageQueueClustersClient()

    def setUp(self):
        super(ClusterTest, self).setUp()
        self.cluster = self._create_cluster()

    def tearDown(self):
        super(ClusterTest, self).tearDown()
        self.client.delete_cluster(self.cluster['id'])

    def _create_cluster(self):
        name = data_utils.rand_name(ClusterTest.__name__ + '-cluster')
        network_id = [self.client.private_network['id']]
        flavor = CONF.message_queue.flavor
        return self.client.create_cluster(name, flavor, network_id)

    def test_list_clusters(self):
        clusters = self.client.list_clusters()
        self.assertIn('id', clusters.data)
        self.assertIn('status', clusters.data)

    def test_get_cluster(self):
        cluster_resp = self.client.get_cluster_details(self.cluster['id'])
        self.assertEqual(self.cluster['id'], cluster_resp['id'])
        self.assertEqual(self.cluster['name'], cluster_resp['name'])

    # Note:  adding a None or Int to this list will generate a
    # tempest_lib.exceptions.ServerFault exception.
    def test_create_cluster_invalid_request_body(self):

        bad_request_bodies = ['Not a post body', [], {}]

        for bad in bad_request_bodies:
            self.assertRaises(tempest_exceptions.BadRequest,
                              self.client.create_cluster_from_body,
                              bad)

    # Not specifying volume_size does not throw a BadRequest exception
    # Todo https://bugs.launchpad.net/cue/+bug/1452980
    def test_create_cluster_missing_attributes(self):
        # Missing Name
        post_body = {
            'size': 1,
            'flavor': '8795',
            'volume_size': 100,
            'network_id': [u'3f21e8ec-5e29-4723-ac87-51f303570c0c']
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

        # Missing Size
        post_body = {
            'name': 'fake name',
            'flavor': '8795',
            'volume_size': 100,
            'network_id': [u'3f21e8ec-5e29-4723-ac87-51f303570c0c']
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

        # Missing Flavor
        post_body = {
            'name': 'fake name',
            'size': 1,
            'volume_size': 100,
            'network_id': [u'3f21e8ec-5e29-4723-ac87-51f303570c0c']
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

        # Missing Network Id
        post_body = {
            'name': 'fake name',
            'size': 1,
            'flavor': '8795',
            'volume_size': 100
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

    # Properly formatted but non-existent net ids don't cause exceptions
    # Todo https://bugs.launchpad.net/cue/+bug/1452980
    def test_create_cluster_invalid_network_id(self):

        post_body = {
            'name': 'fake name',
            'size': 1,
            'flavor': '8795',
            'volume_size': 100,
            'network_id': 'Invalid Network ID'
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

        # Properly formatted non-existent net Ids don't cause exceptions
        # post_body['network_id'] = [u'00000000-0000-0000-0000-000000000000']
        # self.assertRaises(tempest_exceptions.BadRequest,
        #                   self.client.create_cluster_from_body,
        #                   post_body)

    def test_create_cluster_invalid_cluster_size(self):
        post_body = {
            'name': 'fake name',
            'size': 0,
            'flavor': '8795',
            'volume_size': 100,
            'network_id': [u'3f21e8ec-5e29-4723-ac87-51f303570c0c']
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

        post_body['size'] = -1
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

        # Non-numeric strings throws a tempest_lib.exceptions.ServerFault
        # post_body['size'] = 'one'
        # self.assertRaises(tempest_exceptions.BadRequest,
        #                   self.client.create_cluster_from_body,
        #                   post_body)

    # Passing in a flavor Id that doesn't exist (like '0' or 'bad flavor')
    # doesn't fail
    # Todo https://bugs.launchpad.net/cue/+bug/1452980
    def test_create_cluster_invalid_flavors(self):

        # Int flavor should fail
        post_body = {
            'name': 'fake name',
            'size': 1,
            'flavor': 0,
            'volume_size': 100,
            'network_id': [u'3f21e8ec-5e29-4723-ac87-51f303570c0c']
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

        # Non-existent flavor id should throw exception, but doesn't.
        # post_body['flavor'] = '0'
        # self.assertRaises(tempest_exceptions.BadRequest,
        #                   self.client.create_cluster_from_body,
        #                   post_body)

    def test_list_clusters_invalid_uri(self):

        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.list_clusters,
                          url='fake_url')