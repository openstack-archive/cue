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
import time
import uuid

import paramiko
import tempest_lib.base
from tempest_lib.common.utils import data_utils
from tempest_lib import exceptions as tempest_exceptions

from tests.integration.api.v1.clients import clusters_client
from tests.integration.common import client
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

    def tearDown(self):
        super(ClusterTest, self).tearDown()

    def _create_cluster(self):
        name = data_utils.rand_name(ClusterTest.__name__ + '-cluster')
        network_id = [self.client.private_network['id']]
        flavor = CONF.message_queue.flavor
        size = 3
        return self.client.create_cluster(name, size, flavor, network_id)

    def test_create_cluster(self):
        """Test create cluster and verifies cluster goes to ACTIVE state."""
        cluster = self._create_cluster()

        start_time = time.time()
        while True:
            cluster_resp = self.client.get_cluster(cluster['id'])
            if cluster_resp['status'] != 'BUILDING':
                break
            self.assertEqual(cluster_resp['status'], 'BUILDING',
                             'Create cluster failed')
            time.sleep(1)
            if time.time() - start_time > 1800:
                self.get_logs(cluster_resp['id'])
                self.fail('Waited 30 minutes for cluster to get ACTIVE')
        self.assertEqual(cluster_resp['status'], 'ACTIVE',
                         'Create cluster failed')

        # List clusters
        clusters = self.client.list_clusters()
        self.assertIn('id', clusters.data, 'List cluster failed')
        self.assertIn('status', clusters.data, 'List cluster failed')

        # Get cluster
        cluster_resp = self.client.get_cluster(cluster['id'])
        self.assertEqual(cluster['id'], cluster_resp['id'],
                         'Get cluster failed')
        self.assertEqual(cluster['name'], cluster_resp['name'],
                         'Get cluster failed')
        self.assertEqual(cluster['network_id'],
                         cluster_resp['network_id'],
                         'Get cluster failed')
        self.assertEqual(cluster['size'], cluster_resp['size'],
                         'Get cluster failed')

        # Delete cluster
        self.client.delete_cluster(cluster['id'])
        while True:
            try:
                cluster_resp = self.client.get_cluster(cluster['id'])
            except Exception as e:
                self.assertEqual('Object not found', e.message,
                                 'Delete cluster failed')
                break
            self.assertEqual(cluster_resp['status'], 'DELETING',
                             'Delete cluster failed')
            time.sleep(1)
            if time.time() - start_time > 900:
                self.fail('Waited 15 minutes for cluster to be deleted')

    @staticmethod
    def get_logs(cluster_id=None):
        admin_client = client.ServerClient()
        nodes = admin_client.get_cluster_nodes(cluster_id)
        for node in nodes['servers']:
            try:
                if node['addresses']['cue_management_net']:
                    ip = node['addresses']['cue_management_net'][0]['addr']
                else:
                    ip = "N/A"
                print("SSHing to %s, IP: %s" % (node['name'], ip))
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username='ubuntu')
                stdin, stdout, stderr = ssh.exec_command(
                    "tail -n +1 /var/log/rabbitmq/*")
                print("Printing all logs in /var/log/rabbitmq/")
                result = stdout.readlines()
                print(''.join(result))
                ssh.close()
            except Exception:
                print("Could not SSH to %s, IP: %s" % (node['name'], ip))

    def test_create_cluster_invalid_request_body(self):
        """Verify create cluster request with invalid request body."""

        # Note:  adding a None or Int to this list will generate a
        # tempest_lib.exceptions.ServerFault exception.
        bad_request_bodies = ['Not a post body', [], {}]

        for bad in bad_request_bodies:
            self.assertRaises(tempest_exceptions.BadRequest,
                              self.client.create_cluster_from_body,
                              bad)

    def test_create_cluster_missing_name(self):
        """Verify create cluster request with missing name field."""

        post_body = {
            'size': 1,
            'flavor': '8795',
            'volume_size': 100,
            'network_id': [str(uuid.uuid4())]
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

    def test_create_cluster_missing_size(self):
        """Verify create cluster request with missing size field."""

        post_body = {
            'name': 'fake name',
            'flavor': '8795',
            'volume_size': 100,
            'network_id': [str(uuid.uuid4())]
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

    def test_create_cluster_missing_flavor(self):
        """Verify create cluster request with missing flavor field."""

        post_body = {
            'name': 'fake name',
            'size': 1,
            'volume_size': 100,
            'network_id': [str(uuid.uuid4())]
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

    def test_create_cluster_missing_network_id(self):
        """Verify create cluster request with missing network_id field."""

        post_body = {
            'name': 'fake name',
            'size': 1,
            'flavor': '8795',
            'volume_size': 100
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

    def test_create_cluster_invalid_network_id(self):
        """Verifies bad request response for invalid network_id."""

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
        # TODO(Daniel Allegood) https://bugs.launchpad.net/cue/+bug/1452980
        # post_body['network_id'] = [u'00000000-0000-0000-0000-000000000000']
        # self.assertRaises(tempest_exceptions.BadRequest,
        #                  self.client.create_cluster_from_body, post_body)

    def test_create_cluster_invalid_cluster_size(self):
        """Verifies bad request response for invalid size."""

        post_body = {
            'name': 'fake name',
            'size': 0,
            'flavor': '8795',
            'volume_size': 100,
            'network_id': [str(uuid.uuid4())]
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

        post_body['size'] = -1
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

        # Non-numeric strings throws a tempest_lib.exceptions.ServerFault
        # TODO(Daniel Allegood) https://bugs.launchpad.net/cue/+bug/1452980
        # post_body['size'] = 'one'
        # self.assertRaises(tempest_exceptions.BadRequest,
        #                   self.client.create_cluster_from_body,
        #                   post_body)

    def test_create_cluster_invalid_flavors(self):
        """Verifies bad request response for invalid flavor."""

        # Int flavor should fail
        post_body = {
            'name': 'fake name',
            'size': 1,
            'flavor': 0,
            'volume_size': 100,
            'network_id': [str(uuid.uuid4())]
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

        # Non-existent flavor id should throw exception, but doesn't.
        # TODO(Daniel Allegood) https://bugs.launchpad.net/cue/+bug/1452980
        # post_body['flavor'] = '0'
        # self.assertRaises(tempest_exceptions.BadRequest,
        #                   self.client.create_cluster_from_body,
        #                   post_body)

    def test_list_clusters_invalid_uri(self):
        """Verifies Not found response for invalid URI."""

        self.assertRaises(tempest_exceptions.NotFound,
                          self.client.list_clusters,
                          url='fake_url')