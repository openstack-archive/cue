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
Tests for the API Cluster and Endpoint objects.
"""
from wsme import exc as wsme_exception
from wsme.rest import json as rest_json

from cue.api.controllers.v1 import cluster as api_cluster
from cue.tests.unit import base


class TestClusterObject(base.UnitTestCase):

    def setUp(self):
        super(TestClusterObject, self).setUp()

    def test_api_cluster(self):
        """test cluster object with valid input."""
        cluster_value = {
            "network_id": "df295159-ddd4-48e1-bb1b-42248ae96581",
            "flavor": "1",
            "name": "test_cluster",
            "size": 3,
        }
        cluster = api_cluster.Cluster(**cluster_value)

        self.assertEqual(cluster_value['network_id'], cluster.network_id)
        self.assertEqual(cluster_value['flavor'], cluster.flavor)
        self.assertEqual(cluster_value['name'], cluster.name)
        self.assertEqual(cluster_value['size'], cluster.size)

    def test_api_cluster_invalid_type_network_id(self):
        """test cluster object with invalid type 'network_id'."""
        cluster_value = {
            "network_id": ["df295159-ddd4-48e1-bb1b-42248ae96581"],
            "flavor": "1",
            "name": "test_cluster",
            "size": "3",
        }
        self.assertRaises(wsme_exception.InvalidInput,
                          lambda: api_cluster.Cluster(**cluster_value))

    def test_api_cluster_invalid_type_size(self):
        """test cluster object with invalid type 'size'."""
        cluster_value = {
            "network_id": "df295159-ddd4-48e1-bb1b-42248ae96581",
            "flavor": "1",
            "name": "test_cluster",
            "size": "three",
        }
        self.assertRaises(wsme_exception.InvalidInput,
                          lambda: api_cluster.Cluster(**cluster_value))

    def test_api_cluster_invalid_type_volume_size(self):
        """test cluster object with invalid type 'volume_size'."""
        cluster_value = {
            "network_id": "df295159-ddd4-48e1-bb1b-42248ae96581",
            "flavor": "1",
            "name": "test_cluster",
            "size": 3,
            "volume_size": "zero"
        }
        self.assertRaises(wsme_exception.InvalidInput,
                          lambda: api_cluster.Cluster(**cluster_value))

    def test_api_cluster_missing_size(self):
        """test cluster object with missing mandatory field 'size'."""
        cluster_value = {

            "flavor": "1",
            "name": "test_cluster"
        }
        self.assertRaises(wsme_exception.InvalidInput,
                          lambda: rest_json.fromjson(api_cluster.Cluster,
                                                     cluster_value))

    def test_api_cluster_missing_network_id(self):
        """test cluster object with missing mandatory field 'network_id'."""
        cluster_value = {
            "flavor": "1",
            "name": "test_cluster",
            "size": 3
        }
        self.assertRaises(wsme_exception.InvalidInput,
                          lambda: rest_json.fromjson(api_cluster.Cluster,
                                                     cluster_value))

    def test_api_cluster_missing_name(self):
        """test cluster object with missing mandatory field 'name'."""
        cluster_value = {
            "network_id": "df295159-ddd4-48e1-bb1b-42248ae96581",
            "flavor": "1",
            "size": 3
        }
        self.assertRaises(wsme_exception.InvalidInput,
                          lambda: rest_json.fromjson(api_cluster.Cluster,
                                                     cluster_value))

    def test_api_cluster_missing_flavor(self):
        """test cluster object with missing mandatory field 'flavor'."""
        cluster_value = {
            "network_id": "df295159-ddd4-48e1-bb1b-42248ae96581",
            "name": "test_cluster",
            "size": 3
        }
        self.assertRaises(wsme_exception.InvalidInput,
                          lambda: rest_json.fromjson(api_cluster.Cluster,
                                                     cluster_value))

    def test_api_cluster_set_readonly_id(self):
        """test cluster object for read-only 'id' field."""
        cluster_value = {
            "id": "2b40ef88-e267-11e4-8a00-1681e6b88ec1",
            "network_id": "df295159-ddd4-48e1-bb1b-42248ae96581",
            "name": "test_cluster",
            "size": 3,
            "flavor": "1"
        }
        self.assertRaises(wsme_exception.InvalidInput,
                          lambda: rest_json.fromjson(api_cluster.Cluster,
                                                     cluster_value))

    def test_api_cluster_set_readonly_status(self):
        """test cluster object for read-only 'status' field."""
        cluster_value = {
            "network_id": "df295159-ddd4-48e1-bb1b-42248ae96581",
            "name": "test_cluster",
            "size": 3,
            "flavor": "1",
            "status": "BUILDING"
        }
        self.assertRaises(wsme_exception.InvalidInput,
                          lambda: rest_json.fromjson(api_cluster.Cluster,
                                                     cluster_value))

    def tearDown(self):
        super(TestClusterObject, self).tearDown()


class TestEndpointObject(base.UnitTestCase):

    def setUp(self):
        super(TestEndpointObject, self).setUp()

    def test_api_endpoint(self):
        """test endpoint object with valid input."""
        endpoint_value = {
            "type": "public",
            "uri": "http://test-uri",
        }

        endpoint = api_cluster.EndPoint(**endpoint_value)

        self.assertEqual(endpoint_value['type'], endpoint.type)
        self.assertEqual(endpoint_value['uri'], endpoint.uri)

    def tearDown(self):
        super(TestEndpointObject, self).tearDown()