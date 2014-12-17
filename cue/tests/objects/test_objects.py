# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Authors: Davide Agnello <davide.agnello@hp.com>
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
Tests for cue objects classes.
"""
from oslo.utils import timeutils

from cue.api.controllers import v1
from cue.db import api as db_api
from cue.db.sqlalchemy import models
from cue import objects
from cue.tests import base
from cue.tests import utils as test_utils


class ClusterObjectsTests(base.TestCase):
    dbapi = db_api.get_instance()

    def validate_cluster_values(self, cluster_reference, cluster_compare):
        self.assertEqual(cluster_reference.id, cluster_compare.id,
                         "Invalid cluster id value")
        self.assertEqual(cluster_reference.network_id,
                         cluster_compare.network_id,
                         "Invalid cluster network_id value")
        self.assertEqual(cluster_reference.name, cluster_compare.name,
                         "Invalid cluster name value")
        self.assertEqual(cluster_reference.status, cluster_compare.status,
                         "Invalid cluster status value")
        self.assertEqual(cluster_reference.flavor, cluster_compare.flavor,
                         "Invalid cluster flavor value")
        self.assertEqual(cluster_reference.size, cluster_compare.size,
                         "Invalid cluster size value")
        self.assertEqual(cluster_reference.volume_size,
                         cluster_compare.volume_size,
                         "Invalid cluster volume_size value")
        self.assertIn(unicode(cluster_reference.created_at.isoformat()),
                      unicode(cluster_compare.created_at.isoformat()),
                      "Invalid cluster created_at value")
        self.assertIn(unicode(cluster_reference.updated_at.isoformat()),
                      unicode(cluster_compare.updated_at.isoformat()),
                      "Invalid cluster updated_at value")

    def test_cluster_api_to_object_to_api(self):
        """Tests Cluster api object conversion to Cluster object and back

        to api object.
        """
        api_cluster = test_utils.create_api_test_cluster_all()
        object_cluster = objects.Cluster(**api_cluster.as_dict())
        self.validate_cluster_values(api_cluster, object_cluster)
        api_cluster_2 = v1.Cluster(**object_cluster.as_dict())
        self.validate_cluster_values(api_cluster, api_cluster_2)

    def test_cluster_db_to_object_to_db(self):
        """Tests Cluster db object conversion to Cluster object and back

        to db object.
        """
        db_cluster_object = test_utils.create_db_test_cluster_model_object(
                            deleted_at=timeutils.utcnow(), deleted=True)
        object_cluster = objects.Cluster._from_db_object(objects.Cluster(),
                                                         db_cluster_object)
        self.validate_cluster_values(db_cluster_object, object_cluster)
        self.assertEqual(db_cluster_object.deleted,
                        object_cluster.deleted,
                        "Invalid cluster deleted_at value")
        self.assertIn(unicode(db_cluster_object.deleted_at.isoformat()),
                     unicode(object_cluster.deleted_at.isoformat()),
                     "Invalid cluster deleted_at value")

        cluster_changes = object_cluster.obj_get_changes()
        db_cluster_object_2 = models.Cluster()
        db_cluster_object_2.update(cluster_changes)
        self.validate_cluster_values(db_cluster_object, db_cluster_object_2)
        self.assertEqual(db_cluster_object.deleted,
                        db_cluster_object_2.deleted,
                        "Invalid cluster deleted_at value")
        self.assertIn(unicode(db_cluster_object.deleted_at.isoformat()),
                      unicode(db_cluster_object_2.deleted_at.isoformat()),
                      "Invalid cluster deleted_at value")


class NodeObjectsTests(base.TestCase):
    dbapi = db_api.get_instance()

    def test_node_api_to_object_to_api(self):
        """Tests Node api object conversion to Node object and back

        to api object.
        """

    def test_node_db_to_object_to_db(self):
        """Tests Node db object conversion to Node object and back

        to db object.
        """


class EndpointObjectsTests(base.TestCase):
    dbapi = db_api.get_instance()

    def test_endpoint_api_to_object_to_api(self):
        """Tests Endpoint api object conversion to Endpoint object and back

        to api object.
        """

    def test_endpoint_db_to_object_to_db(self):
        """Tests Endpoint db object conversion to Endpoint object and back

        to db object.
        """


class ClusterObjectsApiTests(base.TestCase):
    def test_create_cluster(self):
        """Tests creating a Cluster from Cluster objects API."""

    def test_get_clusters(self):
        """Tests getting all Clusters from Cluster objects API."""

    def test_get_clusters_by_id(self):
        """Tests get Cluster by id from Cluster objects API."""

    def test_mark_cluster_as_delete(self):
        """Tests marking clusters for delete from Cluster objects API."""


class NodeObjectsApiTests(base.TestCase):
    def test_get_nodes_by_cluster_id(self):
        """Tests get nodes by cluster id from Nodes objects API."""


class EndpointObjectsApiTests(base.TestCase):
    def test_get_endpoints_by_node_id(self):
        """Tests get endpoint objects by node id from Endpoint objects API."""