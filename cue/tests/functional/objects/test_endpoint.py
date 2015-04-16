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
Tests for cue endpoint object.
"""
from oslo_db import exception as oslo_exception

from cue.api.controllers.v1 import cluster
from cue.db import api as db_api
from cue.db.sqlalchemy import models
from cue import objects
from cue.tests.functional import base
from cue.tests.functional import utils as func_utils


class EndpointObjectsTests(base.FunctionalTestCase):
    dbapi = db_api.get_instance()

    def create_object_endpoint(self, node_id):
        """Create an endpoint object for the given node."""
        endpoint_dict = func_utils.get_test_endpoint(node_id=node_id)
        api_endpoint = objects.Endpoint(**endpoint_dict)
        self.validate_endpoint_values(endpoint_dict, api_endpoint)
        api_endpoint.create(self.context)

        new_endpoint = self.dbapi.get_endpoints_in_node(self.context,
                                                        api_endpoint.node_id)
        return new_endpoint[0]

    def validate_endpoint_values(self, endpoint_ref, endpoint_cmp):
        """Validate Endpoint Object fields."""
        if not (isinstance(endpoint_ref, cluster.EndPoint) or
                isinstance(endpoint_cmp, cluster.EndPoint)):
            self.assertEqual(endpoint_ref.id if hasattr(endpoint_ref, "id")
                             else endpoint_ref["id"],
                             endpoint_cmp.id if hasattr(endpoint_cmp, "id")
                             else endpoint_cmp["id"],
                             "Invalid endpoint id value")
            self.assertEqual(endpoint_ref.node_id if hasattr(endpoint_ref,
                             "node_id") else endpoint_ref["node_id"],
                             endpoint_cmp.node_id if hasattr(endpoint_cmp,
                             "node_id") else endpoint_cmp["node_id"],
                             "Invalid endpoint node_id value")
        self.assertEqual(endpoint_ref.uri if hasattr(endpoint_ref, "uri") else
                         endpoint_ref["uri"],
                         endpoint_cmp.uri if hasattr(endpoint_cmp, "uri") else
                         endpoint_cmp["uri"],
                         "Invalid endpoint uri value")
        self.assertEqual(endpoint_ref.type if hasattr(endpoint_ref, "type")
                         else endpoint_ref["type"],
                         endpoint_cmp.type if hasattr(endpoint_cmp, "type")
                         else endpoint_cmp["type"],
                         "Invalid endpoint type value")

    def test_endpoint_object_generation(self):
        """Test Endpoint Object generation from a cluster dictionary object."""
        endpoint_dict = func_utils.get_test_endpoint()
        endpoint_object = objects.Endpoint(**endpoint_dict)
        self.validate_endpoint_values(endpoint_dict, endpoint_object)

    def test_endpoint_api_to_object_to_api(self):
        """Tests Endpoint api object conversion to Endpoint object and back

        to api object.
        """
        endpoint_dict = func_utils.get_test_endpoint()
        api_endpoint = cluster.EndPoint(**endpoint_dict)
        object_endpoint = objects.Endpoint(**endpoint_dict)
        self.validate_endpoint_values(api_endpoint, object_endpoint)
        api_endpoint_2 = cluster.EndPoint(**object_endpoint.as_dict())
        self.validate_endpoint_values(api_endpoint, api_endpoint_2)

    def test_endpoint_db_to_object_to_db(self):
        """Tests Endpoint db object conversion to Endpoint object and back

        to db object.
        """
        endpoint_dict = func_utils.get_test_endpoint()
        db_endpoint_object = models.Endpoint()
        db_endpoint_object.update(endpoint_dict)
        object_endpoint = objects.Endpoint._from_db_object(objects.Endpoint(),
                                                           db_endpoint_object)
        self.validate_endpoint_values(db_endpoint_object, object_endpoint)

        endpoint_changes = object_endpoint.obj_get_changes()
        db_endpoint_object_2 = models.Endpoint()
        db_endpoint_object_2.update(endpoint_changes)
        self.validate_endpoint_values(db_endpoint_object, db_endpoint_object_2)

    def test_create(self):
        """Tests create an endpoint from Endpoint objects API."""
        new_cluster = func_utils.create_object_cluster(self.context)
        cluster_nodes = self.dbapi.get_nodes_in_cluster(self.context,
                                                        new_cluster.id)
        endpoint_dict = func_utils.get_test_endpoint(
            node_id=cluster_nodes[0].id)
        endpoint = objects.Endpoint(**endpoint_dict)
        self.validate_endpoint_values(endpoint_dict, endpoint)
        endpoint.create(self.context)
        new_endpoint = self.dbapi.get_endpoints_in_node(self.context,
                                                        endpoint.node_id)
        self.validate_endpoint_values(endpoint, new_endpoint[0])

    def test_create_without_valid_node(self):
        """Tests create an endpoint for a non-existing cluster from Endpoint

        objects API.
        """
        api_endpoint_dict = func_utils.get_test_endpoint()
        api_endpoint = objects.Endpoint(**api_endpoint_dict)
        self.validate_endpoint_values(api_endpoint_dict, api_endpoint)
        self.assertRaises(oslo_exception.DBReferenceError, api_endpoint.create,
                          self.context)

    def test_update_by_node_id(self):
        """Tests update endpoint by node id from Endpoint objects API."""
        new_cluster = func_utils.create_object_cluster(self.context, size=1)
        cluster_node = self.dbapi.get_nodes_in_cluster(self.context,
                                                        new_cluster.id)
        cluster_node_id = cluster_node[0].id
        new_endpoint = self.create_object_endpoint(cluster_node_id)
        endpoint_values = {
            'uri': '10.0.0.2:5672',
            'type': 'XMPP'
        }
        objects.Endpoint.update_by_node_id(self.context, new_endpoint.node_id,
                                           endpoint_values)
        endpoints = self.dbapi.get_endpoints_in_node(self.context,
                                                     new_endpoint.node_id)
        for endpoint in endpoints:
            self.assertEqual('XMPP', endpoint.type)
            self.assertEqual('10.0.0.2:5672', endpoint.uri)

    def test_get_endpoints_by_node_id(self):
        """Tests  get endpoint by node id from Endpoint objects API."""
        new_cluster = func_utils.create_object_cluster(self.context, size=1)
        cluster_node = self.dbapi.get_nodes_in_cluster(self.context,
                                                        new_cluster.id)
        node_id = cluster_node[0].id
        new_endpoint = self.create_object_endpoint(node_id)
        endpoint_list = objects.Endpoint.get_endpoints_by_node_id(
            self.context, new_endpoint.node_id)
        for endpoint in endpoint_list:
            self.validate_endpoint_values(endpoint, new_endpoint)