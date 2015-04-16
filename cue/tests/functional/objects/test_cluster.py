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
Tests for cue cluster object.
"""
import uuid

import mock
from oslo.utils import timeutils
import testtools

from cue.api.controllers.v1 import cluster
from cue.common import exception
from cue.db import api as db_api
from cue.db.sqlalchemy import models
from cue import objects
from cue.tests.functional import base
from cue.tests.functional import utils as func_utils
from cue.tests import utils as test_utils


class ClusterObjectsTests(base.FunctionalTestCase):
    dbapi = db_api.get_instance()

    def validate_cluster_deleted_fields(self, cluster_ref, cluster_cmp):
        """Validate Cluster Object deleted and deleted_at fields."""
        self.assertEqual(cluster_ref.deleted, cluster_cmp.deleted,
                         "Invalid cluster deleted value")
        self.assertTrue(test_utils.compare_dates(cluster_ref.deleted_at
                        if hasattr(cluster_ref, "deleted_at")
                        else cluster_ref["deleted_at"],
                        cluster_cmp.deleted_at
                        if hasattr(cluster_cmp, "deleted_at")
                        else cluster_cmp["deleted_at"]),
                        "Invalid cluster deleted_at value")

    def test_cluster_object_generation(self):
        """Test Cluster Object generation from a cluster dictionary object."""
        cluster_dict = func_utils.get_test_cluster()
        cluster_object = objects.Cluster(**cluster_dict)
        test_utils.validate_cluster_values(self, cluster_dict, cluster_object)

    def test_cluster_api_to_object_to_api(self):
        """Tests Cluster api object conversion to Cluster object and back

        to api object.
        """
        # create cluster api object
        api_cluster = func_utils.create_api_test_cluster_all().as_dict()
        # adjust network_id from list to single value
        api_cluster['network_id'] = api_cluster['network_id'][0]
        # create cue cluster object from api cluster object
        object_cluster = objects.Cluster(**api_cluster).as_dict()
        # verify fields match
        test_utils.validate_cluster_values(self, api_cluster, object_cluster)

        # adjust network_id from single value back to list
        object_cluster['network_id'] = [object_cluster['network_id']]
        # create cluster api object from cue cluster object
        api_cluster_2 = cluster.Cluster(**object_cluster).as_dict()
        # verify fields match to initial api cluster object
        test_utils.validate_cluster_values(self, api_cluster, api_cluster_2)

    def test_cluster_db_to_object_to_db(self):
        """Tests Cluster db object conversion to Cluster object and back

        to db object.
        """
        db_cluster_object = func_utils.create_db_test_cluster_model_object(
            self.context, deleted_at=timeutils.utcnow(), deleted=True)
        object_cluster = objects.Cluster._from_db_object(objects.Cluster(),
                                                         db_cluster_object)

        test_utils.validate_cluster_values(self, db_cluster_object,
                                           object_cluster)
        self.validate_cluster_deleted_fields(db_cluster_object,
                                             object_cluster)

        cluster_changes = object_cluster.obj_get_changes()
        db_cluster_object_2 = models.Cluster()
        db_cluster_object_2.update(cluster_changes)
        test_utils.validate_cluster_values(self, db_cluster_object,
                                           db_cluster_object_2)
        self.validate_cluster_deleted_fields(db_cluster_object,
                                             db_cluster_object_2)

    def test_create_cluster_size_one(self):
        """Tests create cluster from Cluster objects API."""
        test_cluster_dict = func_utils.get_test_cluster(size=1)
        new_cluster = objects.Cluster(**test_cluster_dict)
        test_utils.validate_cluster_values(self, test_cluster_dict,
                                           new_cluster)
        new_cluster.create(self.context)
        db_cluster = self.dbapi.get_cluster_by_id(self.context, new_cluster.id)
        test_utils.validate_cluster_values(self, new_cluster, db_cluster)
        cluster_node = self.dbapi.get_nodes_in_cluster(self.context,
                                                        db_cluster.id)

        # check if cluster size is one before accessing the node
        self.assertEqual(1, len(cluster_node))
        self.assertEqual(db_cluster.id, cluster_node[0].cluster_id)
        self.assertEqual(db_cluster.flavor, cluster_node[0].flavor)
        self.assertEqual(db_cluster.status, cluster_node[0].status)

    def test_create_cluster_size_three(self):
        """Tests create cluster of size three from Cluster objects API."""
        test_cluster_dict = func_utils.get_test_cluster(size=3)
        new_cluster = objects.Cluster(**test_cluster_dict)
        test_utils.validate_cluster_values(self, test_cluster_dict,
                                           new_cluster)
        new_cluster.create(self.context)
        db_cluster = self.dbapi.get_cluster_by_id(self.context,
                                                  new_cluster.id)
        test_utils.validate_cluster_values(self, new_cluster, db_cluster)

        cluster_nodes = self.dbapi.get_nodes_in_cluster(self.context,
                                                        db_cluster.id)
        for nodes in cluster_nodes:
            self.assertEqual(db_cluster.id, nodes.cluster_id)
            self.assertEqual(db_cluster.flavor, nodes.flavor)
            self.assertEqual(db_cluster.status, nodes.status)

    def test_update_cluster(self):
        """Tests update cluster from Cluster objects API."""
        new_cluster = func_utils.create_object_cluster(
            self.context, name='test_cluster', flavor='flavor1')
        new_cluster.flavor = 'flavor2'
        new_cluster.name = 'test_cluster1'
        new_cluster.update(self.context, new_cluster.id)

        updated_cluster = self.dbapi.get_cluster_by_id(self.context,
                                                       new_cluster.id)
        # check update fields
        self.assertEqual('flavor2', updated_cluster.flavor)
        self.assertEqual('test_cluster1', updated_cluster.name)
        # check unchanged fields fields
        self.assertEqual(new_cluster.id, updated_cluster.id)
        self.assertEqual(new_cluster.network_id, updated_cluster.network_id)
        self.assertEqual(new_cluster.status, updated_cluster.status)
        self.assertEqual(new_cluster.size, updated_cluster.size)

    def test_get_cluster_list_size_one(self):
        """Tests list Cluster of size one from Cluster objects API."""
        new_cluster = func_utils.create_object_cluster(self.context)
        cluster_list = objects.Cluster.get_clusters(self.context)
        test_utils.validate_cluster_values(self, cluster_list[0], new_cluster)

    def test_get_cluster_list_size_three(self):
        """Tests list Clusters of size three from Cluster objects API."""
        cluster_list = list()
        for list_size in range(3):
            new_cluster = func_utils.create_object_cluster(
                self.context, id=str(uuid.uuid4()))
            cluster_list.append(new_cluster)

        returned_cluster_list = objects.Cluster.get_clusters(self.context)

        for returned_clusterobj, clusterobj in zip(returned_cluster_list,
                                                   cluster_list):
            test_utils.validate_cluster_values(self, returned_clusterobj,
                                               clusterobj)

    def test_get_cluster_by_id(self):
        """Tests get Cluster by id from Cluster objects API."""
        new_cluster = func_utils.create_object_cluster(self.context)
        test_cluster = objects.Cluster.get_cluster_by_id(self.context,
                                                         new_cluster.id)
        test_utils.validate_cluster_values(self, new_cluster, test_cluster)

    def test_get_nonexistent_cluster(self):
        """Tests get cluster from Cluster objects API for nonexistent cluster.

        """
        func_utils.create_object_cluster(self.context)
        nonexistent_cluster_id = '17efe8ae-e93c-11e4-b02c-1681e6b88ec1'
        self.assertRaises(exception.NotFound,
                          objects.Cluster.get_cluster_by_id,
                          self.context, nonexistent_cluster_id)

    def test_update_cluster_deleting(self):
        """Tests delete from Cluster objects API."""
        new_cluster = func_utils.create_object_cluster(self.context)
        objects.Cluster.update_cluster_deleting(self.context, new_cluster.id)
        deleted_cluster = self.dbapi.get_cluster_by_id(self.context,
                                                       new_cluster.id)

        self.assertEqual('DELETING', deleted_cluster.status)

    def test_update_cluster_deleting_invalid_id(self):
        """Tests delete from Cluster objects API with invalid cluster id."""
        func_utils.create_object_cluster(self.context)
        invalid_cluster_id = '17efe8ae-e93c-11e4-b02c-1681e6b88ec1'
        self.assertRaises(exception.NotFound,
                          objects.Cluster.update_cluster_deleting,
                          self.context, invalid_cluster_id)

    def test_get_cluster_by_id_forbidden(self):
        """Tests get Cluster by id with invalid tenant."""
        api_cluster = func_utils.create_object_cluster(self.context)
        tenant_b = self.get_context(tenant='b')

        with mock.patch.object(
            objects.Cluster.dbapi, 'get_cluster_by_id',
                return_value=api_cluster):
            with testtools.ExpectedException(exception.NotAuthorized):
                objects.Cluster.get_cluster_by_id(tenant_b, api_cluster.id)

    def test_update_cluster_deleting_forbidden(self):
        """Tests delete from Cluster objects API with invalid tenant."""
        api_cluster = func_utils.create_object_cluster(self.context)
        tenant_b = self.get_context(tenant='b')

        with mock.patch.object(
            objects.Cluster.dbapi, 'get_cluster_by_id',
                return_value=api_cluster):
            with testtools.ExpectedException(exception.NotAuthorized):
                objects.Cluster.update_cluster_deleting(
                    tenant_b, api_cluster.id)