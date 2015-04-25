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
Cue Integration Test using cue-client binding
"""
import logging
import unittest

from cueclient.v1 import client
from keystoneclient.auth.identity import v2
from keystoneclient import exceptions
from keystoneclient import session as ksc_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cluster Details
# replace with correct network_id
cluster_network_id = "9d6708ee-ea48-4e78-bef6-b50b48405091"
cluster_name = "test_cluster"
cluster_flavor = "8795"
cluster_size = 1

# Keystone Credentials
auth_url = "http://192.168.233.171:5000/v2.0/"
user_name = "admin"
password = "password"
tenant_name = "admin"


class TestCueIntegration(unittest.TestCase):

    def setUp(self):
        super(TestCueIntegration, self).setUp()
        auth = v2.Password(
            auth_url=auth_url,
            username=user_name,
            password=password,
            tenant_name=tenant_name
            )
        session = ksc_session.Session(auth=auth)
        self.cue_client = client.Client(session=session)

    def create_cluster(self):
        """Helper method to create a new cluster."""
        create_response = self.cue_client.clusters.create(
            name=cluster_name, nic=cluster_network_id,
            flavor=cluster_flavor, size=cluster_size, volume_size="0")
        return create_response

    def test_cluster_create(self):
        """test cluster create."""
        logger.info("Running create cluster test")
        create_response = self.cue_client.clusters.create(
            name=cluster_name, nic=cluster_network_id, flavor=cluster_flavor,
            size=cluster_size, volume_size="0")
        self.assertEqual(cluster_name, create_response.name)
        self.assertEqual([cluster_network_id], create_response.network_id)
        self.assertEqual(cluster_flavor, create_response.flavor)
        self.assertEqual(cluster_size, create_response.size)

    def test_cluster_show(self):
        """test cluster show."""
        logger.info("Running show cluster test")
        if len(self.cue_client.clusters.list()) == 0:
            self.create_cluster()
        # select the first cluster info to test
        cluster_selected = self.cue_client.clusters.list()[0]

        show_response = self.cue_client.clusters.get(cluster_selected.id)
        self.assertEqual(cluster_selected.id, show_response.id)
        self.assertEqual(cluster_selected.name, show_response.name)
        self.assertEqual(cluster_selected.size, show_response.size)
        self.assertEqual(cluster_selected.flavor, show_response.flavor)
        self.assertEqual(cluster_selected.network_id, show_response.network_id)

    def test_cluster_list(self):
        """test cluster list."""
        logger.info("Running list cluster test")
        if len(self.cue_client.clusters.list()) == 0:
            self.create_cluster()

        cluster_list = self.cue_client.clusters.list()
        for cluster in cluster_list:
            self.assertEqual([cluster_network_id], cluster.network_id)

    def test_cluster_delete(self):
        """test cluster delete."""
        logger.info("Running delete cluster test")
        if len(self.cue_client.clusters.list()) == 0:
            self.create_cluster()
        cluster_list = self.cue_client.clusters.list()
        cluster_delete_id = cluster_list[0].id
        self.cue_client.clusters.delete(cluster_delete_id)
        try:
            self.assertEqual("DELETING",
                self.cue_client.clusters.get(cluster_delete_id).status)
        except Exception:
            self.assertRaises(exceptions.NotFound,
                              self.cue_client.clusters.get,
                              cluster_delete_id)

    def tearDown(self):
        super(TestCueIntegration, self).tearDown()
