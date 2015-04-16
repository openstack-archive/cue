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
Tests for cue node object.
"""
from cue.db import api as db_api
from cue.db.sqlalchemy import models
from cue import objects
from cue.tests.functional import base
from cue.tests.functional import utils as func_utils
from cue.tests import utils as test_utils


class NodeObjectsTests(base.FunctionalTestCase):
    dbapi = db_api.get_instance()

    def validate_node_values(self, node_ref, node_cmp):
        """Validate Node Object fields."""
        self.assertEqual(node_ref.id if hasattr(node_ref, "id") else
                         node_ref["id"],
                         node_cmp.id if hasattr(node_cmp, "id") else
                         node_cmp["id"],
                         "Invalid node id value")
        self.assertEqual(node_ref.cluster_id if hasattr(node_ref, "cluster_id")
                         else node_ref["cluster_id"],
                         node_cmp.cluster_id if hasattr(node_cmp, "cluster_id")
                         else node_cmp["cluster_id"],
                         "Invalid cluster_id value")
        self.assertEqual(node_ref.instance_id if hasattr(node_ref,
                         "instance_id") else node_ref["instance_id"],
                         node_cmp.instance_id if hasattr(node_cmp,
                         "instance_id") else node_cmp["instance_id"],
                         "Invalid instance_id value")
        self.assertEqual(node_ref.flavor if hasattr(node_ref, "flavor") else
                         node_ref["flavor"],
                         node_cmp.flavor if hasattr(node_cmp, "flavor") else
                         node_cmp["flavor"],
                         "Invalid flavor value")
        self.assertEqual(node_ref.status if hasattr(node_ref, "status") else
                         node_ref["status"],
                         node_cmp.status if hasattr(node_cmp, "status") else
                         node_cmp["status"],
                         "Invalid status value")

        self.assertTrue(test_utils.compare_dates(node_ref["created_at"],
                                                 node_cmp["created_at"]),
                        "Invalid created_at value")

        self.assertTrue(test_utils.compare_dates(node_ref["updated_at"],
                                                 node_cmp["updated_at"]),
                        "Invalid updated_at value")

        self.assertTrue(test_utils.compare_dates(node_ref["deleted_at"],
                                                 node_cmp["deleted_at"]),
                        "Invalid deleted_at value")

    def test_node_object_generation(self):
        """Test Node Object generation from a node dictionary object."""
        node_dict = func_utils.get_test_node()
        node_object = objects.Node(**node_dict)
        self.validate_node_values(node_object, node_dict)

    def test_node_db_to_object_to_db(self):
        """Tests Node db object conversion to Node object and back

        to db object.
        """
        node_dict = func_utils.get_test_node()
        db_node_object = models.Node()
        db_node_object.update(node_dict)
        object_node = objects.Node._from_db_object(objects.Node(),
                                                   db_node_object)
        self.validate_node_values(db_node_object, object_node)

        node_changes = object_node.obj_get_changes()
        db_node_object_2 = models.Endpoint()
        db_node_object_2.update(node_changes)
        self.validate_node_values(db_node_object, db_node_object_2)

    def test_update_node_size_one(self):
        """Tests update node from Node objects API."""
        new_cluster = func_utils.create_object_cluster(self.context)

        db_node = self.dbapi.get_nodes_in_cluster(self.context, new_cluster.id)
        new_node = objects.Node._from_db_object(objects.Node(), db_node[0])
        new_node.flavor = 'flavor2'
        new_node.update(self.context, new_node.id)
        updated_node = self.dbapi.get_nodes_in_cluster(self.context,
                                                       new_cluster.id)[0]
        self.assertEqual('flavor2', updated_node.flavor)

    def test_update_node_size_three(self):
        """Tests update three nodes from Node objects API."""
        new_cluster = func_utils.create_object_cluster(self.context, size=3)

        db_nodes = self.dbapi.get_nodes_in_cluster(self.context,
                                                   new_cluster.id)
        # check if cluster size is 3
        self.assertEqual(3, len(db_nodes))
        for current_node in db_nodes:
            current_node = objects.Node._from_db_object(objects.Node(),
                                                       current_node)
            current_node.flavor = 'flavor2'
            current_node.update(self.context, current_node.id)

        updated_nodes = self.dbapi.get_nodes_in_cluster(self.context,
                                                        new_cluster.id)
        for nodes in updated_nodes:
            self.assertEqual('flavor2', nodes.flavor)

    def test_get_nodes_by_cluster_id(self):
        """Tests get nodes by cluster id from Node objects API."""
        new_cluster = func_utils.create_object_cluster(self.context, size=2)

        db_nodes = self.dbapi.get_nodes_in_cluster(self.context,
                                                   new_cluster.id)
        node_list = objects.Node.get_nodes_by_cluster_id(self.context,
                                                              new_cluster.id)
        for db_node, node in zip(db_nodes, node_list):
            self.validate_node_values(db_node, node)

    def test_get_node_by_id(self):
        """Tests get nodes by node id from Nodes objects API."""
        new_cluster = func_utils.create_object_cluster(self.context)

        db_node = self.dbapi.get_nodes_in_cluster(self.context, new_cluster.id)
        obj_node = objects.Node._from_db_object(objects.Node(), db_node[0])
        node = objects.Node.get_node_by_id(self.context, obj_node.id)
        self.validate_node_values(obj_node, node)