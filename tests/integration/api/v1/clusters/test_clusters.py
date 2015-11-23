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
import sys
import time
import traceback
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

    def _create_cluster(self, username, password):
        name = data_utils.rand_name(ClusterTest.__name__ + '-cluster')
        network_id = [self.client.private_network['id']]
        flavor = CONF.message_broker.flavor
        size = 3
        return self.client.create_cluster(name, size, flavor, network_id,
                                          username=username, password=password)

    def test_create_cluster(self):
        """Test create cluster.

        This test will:
        1. Issue create cluster request
        2. Wait until cluster goes into 'ACTIVE' state
        3. Runs test script in one of three nodes with invalid credentials
        4. Runs test script in one of three nodes with valid credentials
        5. Performs cluster list
        6. Stop first two nodes in cluster (wait until stopped)
        7. Verify Cluster goes to 'DOWN' state
        6. Issues delete cluster request on cluster created on step 1
        7. Waits for cluster to be deleted
        """
        cluster_resp = {'status': 'BUILDING'}
        username = 'rabbitmq'
        password = 'rabbit'
        cluster = self._create_cluster(username, password)

        start_time = time.time()
        cluster_id = 0
        while True:
            cluster_resp = self.client.get_cluster(cluster['id'])
            cluster_id = cluster_resp['id']
            if (cluster_resp['status'] == 'ACTIVE' or
                    cluster_resp['status'] == 'ERROR' or
                    time.time() - start_time >= 1800):
                break
            time.sleep(1)

        if cluster_resp['status'] != 'ACTIVE':
            print("Cluster creation failed, cluster status %s.  Attempting to "
                  "retrieve logs from cluster nodes." % cluster_resp['status'])
            self.get_logs(cluster_id)

        self.assertEqual(cluster_resp['status'], 'ACTIVE',
                         'Create cluster failed')

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

        # Verify invalid and valid rabbitmq credentials
        admin_client = client.ServerClient()
        cluster_nodes = admin_client.get_cluster_nodes(cluster['id'])
        node = cluster_nodes['servers'][0]
        networks = node['addresses']['cue_management_net']
        if networks:
            ip = [n['addr'] for n in networks if n['version'] == 4][0]
        else:
            # Devstack bug where network information is missing.
            # This issue is intermittent.
            print("Could not SSH to %s. Network information is missing"
                  % (node['name']))
        rabbitmq_file = "/opt/rabbitmq_test.py"

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username='ubuntu',
                    key_filename='/tmp/cue-mgmt-key')
        command = "python {0} -H {1} -P {2} -u {3} -p {4}".format(
            rabbitmq_file, ip, '5672', username, "invalid")
        status, stdout, stderr = ssh.exec_command(command)
        self.assertNotEqual(stdout.channel.recv_exit_status(), 0,
                            "Invalid RabbitMQ credentials test failed")

        command = "python {0} -H {1} -P {2} -u {3} -p {4}".format(
            rabbitmq_file, ip, '5672', username, password)
        status, stdout, stderr = ssh.exec_command(command)
        self.assertEqual(stdout.channel.recv_exit_status(), 0,
                         "Valid RabbitMQ credentials test failed")
        ssh.close()

        # List clusters
        clusters = self.client.list_clusters()
        self.assertIn('id', clusters.data, 'List cluster failed')
        self.assertIn('status', clusters.data, 'List cluster failed')

        # Stop the first two servers (cluster nodes)
        for server_index in range(0, 2):
            # Stop server
            admin_client.stop_server(
                cluster_nodes['servers'][server_index]['id'])
            start_time = time.time()
            while True:
                # Wait until server goes to 'SHUTOFF' state
                cluster_nodes = admin_client.get_cluster_nodes(cluster['id'])
                if (cluster_nodes['servers'][server_index]['status'] ==
                        'SHUTOFF'):
                    break
                time.sleep(1)
                if time.time() - start_time > 60:
                    self.fail("Waited 1 minutes for server %s to be stopped"
                              % cluster_nodes['servers'][server_index]['id'])

        # Verify Cluster status goes to DOWN
        start_time = time.time()
        while True:
            # Wait until cluster status goes to DOWN
            try:
                cluster_resp = self.client.get_cluster(cluster['id'])
            except Exception as e:
                self.assertEqual('Object not found', e.message,
                                 'Cluster not found')
                break
            if cluster_resp['status'] == 'DOWN':
                break
            time.sleep(5)
            if time.time() - start_time > 605:
                self.fail('Waited 10 minutes for cluster state to change to: '
                          'DOWN')

        # Delete cluster
        start_time = time.time()
        self.client.delete_cluster(cluster['id'])
        while True:
            # Wait until Cluster is deleted
            try:
                cluster_resp = self.client.get_cluster(cluster['id'])
            except Exception as e:
                self.assertEqual('Object not found', e.message,
                                 'Delete cluster failed')
                break
            self.assertEqual(cluster_resp['status'], 'DELETING',
                             'Delete cluster failed')
            time.sleep(1)
            if time.time() - start_time > 305:
                self.fail('Waited 5 minutes for cluster to be deleted')

    @staticmethod
    def get_logs(cluster_id=None):
        admin_client = client.ServerClient()
        nodes = admin_client.get_cluster_nodes(cluster_id)
        for node in nodes['servers']:
            try:
                # Print server console log
                data = admin_client.get_console_log(node['id']).data
                print("Console log for node %s" % node['name'])
                print(data)

                # SSH to get the rabbitmq logs
                networks = node['addresses']['cue_management_net']
                if networks:
                    ip = [n['addr'] for n in networks if n['version'] == 4][0]
                else:
                    # Devstack bug where network information is missing.
                    # This issue is intermittent.
                    print("Could not SSH to %s. Network information is missing"
                          % (node['name']))
                    continue
                print("SSHing to %s, IP: %s" % (node['name'], ip))
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username='ubuntu',
                            key_filename='/tmp/cue-mgmt-key')
                stdin, stdout, stderr = ssh.exec_command(
                    "tail -n +1 /var/log/rabbitmq/*")
                print("Printing all logs in /var/log/rabbitmq/")
                result = stdout.readlines()
                print(''.join(result))
                ssh.close()
            except Exception:
                print("Could not SSH to %s, IP: %s" % (node['name'], ip))
                traceback.print_exc(file=sys.stdout)

    def test_create_cluster_invalid_request_body(self):
        """Verify create cluster request with invalid request body."""

        self.assertRaises(tempest_exceptions.ServerFault,
                          self.client.create_cluster_from_body,
                          'Not a post body')

        self.assertRaises(tempest_exceptions.ServerFault,
                          self.client.create_cluster_from_body,
                          [])

        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          {})

    def test_create_cluster_missing_name(self):
        """Verify create cluster request with missing name field."""

        post_body = {
            'size': 1,
            'flavor': '8795',
            'volume_size': 100,
            'network_id': [str(uuid.uuid4())],
            'authentication': {'type': 'PLAIN',
                               'token': {'username': 'rabbitmq',
                                         'password': 'rabbit'}}
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
            'network_id': [str(uuid.uuid4())],
            'authentication': {'type': 'PLAIN',
                               'token': {'username': 'rabbitmq',
                                         'password': 'rabbit'}}
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
            'network_id': [str(uuid.uuid4())],
            'authentication': {'type': 'PLAIN',
                               'token': {'username': 'rabbitmq',
                                         'password': 'rabbit'}}
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
            'volume_size': 100,
            'authentication': {'type': 'PLAIN',
                               'token': {'username': 'rabbitmq',
                                         'password': 'rabbit'}}
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
            'network_id': 'Invalid Network ID',
            'authentication': {'type': 'PLAIN',
                               'token': {'username': 'rabbitmq',
                                         'password': 'rabbit'}}
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
            'network_id': [str(uuid.uuid4())],
            'authentication': {'type': 'PLAIN',
                               'token': {'username': 'rabbitmq',
                                         'password': 'rabbit'}}
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
            'network_id': [str(uuid.uuid4())],
            'authentication': {'type': 'PLAIN',
                               'token': {'username': 'rabbitmq',
                                         'password': 'rabbit'}}
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

    def test_create_cluster_missing_authentication(self):
        """Verify create cluster request with missing authentication field."""

        post_body = {
            'name': 'fake name',
            'flavor': '8795',
            'size': 1,
            'volume_size': 100,
            'network_id': [str(uuid.uuid4())]
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

    def test_create_cluster_missing_authentication_type(self):
        """Verify create cluster request with missing authentication type."""

        post_body = {
            'name': 'fake name',
            'flavor': '8795',
            'size': 1,
            'volume_size': 100,
            'network_id': [str(uuid.uuid4())],
            'authentication': {'token': {'username': 'rabbitmq',
                                         'password': 'rabbit'}}
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

    def test_create_cluster_missing_authentication_token(self):
        """Verify create cluster request with missing authentication token."""

        post_body = {
            'name': 'fake name',
            'flavor': '8795',
            'size': 1,
            'volume_size': 100,
            'network_id': [str(uuid.uuid4())],
            'authentication': {'type': 'PLAIN'}
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

    def test_create_cluster_missing_authentication_username(self):
        """Verify create cluster request with missing username."""

        post_body = {
            'name': 'fake name',
            'flavor': '8795',
            'size': 1,
            'volume_size': 100,
            'network_id': [str(uuid.uuid4())],
            'authentication': {'type': 'PLAIN',
                               'token': {'password': 'rabbit'}}
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

    def test_create_cluster_missing_authentication_password(self):
        """Verify create cluster request with missing password."""

        post_body = {
            'name': 'fake name',
            'flavor': '8795',
            'size': 1,
            'volume_size': 100,
            'network_id': [str(uuid.uuid4())],
            'authentication': {'type': 'PLAIN',
                               'token': {'username': 'rabbitmq'}}
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

    def test_create_cluster_invalid_authentication_username(self):
        """Verify create cluster request with invalid username."""

        post_body = {
            'name': 'fake name',
            'flavor': '8795',
            'size': 1,
            'volume_size': 100,
            'network_id': [str(uuid.uuid4())],
            'authentication': {'type': 'PLAIN',
                               'token': {'username': '',
                                         'password': 'rabbit'}}
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)

    def test_create_cluster_invalid_authentication_password(self):
        """Verify create cluster request with invalid password."""

        post_body = {
            'name': 'fake name',
            'flavor': '8795',
            'size': 1,
            'volume_size': 100,
            'network_id': [str(uuid.uuid4())],
            'authentication': {'type': 'PLAIN',
                               'token': {'username': 'rabbitmq',
                                         'password': ''}}
        }
        self.assertRaises(tempest_exceptions.BadRequest,
                          self.client.create_cluster_from_body,
                          post_body)
