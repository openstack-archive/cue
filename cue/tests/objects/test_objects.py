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
import iso8601
import mock
from oslo.utils import timeutils
import testtools

from cue.api.controllers.v1 import cluster
from cue.common import exception
from cue.db import api as db_api
from cue.db.sqlalchemy import models
from cue import objects
from cue.tests import base
from cue.tests import utils as test_utils


class ClusterObjectsTests(base.TestCase):
    dbapi = db_api.get_instance()

    def compare_dates(self, datetime1, datetime2):
        if datetime1.utcoffset() is None:
            datetime1 = datetime1.replace(tzinfo=iso8601.iso8601.Utc())
        if datetime2.utcoffset() is None:
            datetime2 = datetime2.replace(tzinfo=iso8601.iso8601.Utc())
        self.assertEqual(datetime1 == datetime2, True,
                         "Invalid datetime value")

    def validate_cluster_values(self, cluster_ref, cluster_cmp):
        self.assertEqual(cluster_ref.id if hasattr(cluster_ref, "id") else
                         cluster_ref["id"],
                         cluster_cmp.id if hasattr(cluster_cmp, "id") else
                         cluster_cmp["id"],
                         "Invalid cluster id value")
        self.assertEqual(cluster_ref.network_id if hasattr(cluster_ref,
                                                           "network_id")
                         else cluster_ref["network_id"],
                         cluster_cmp.network_id if hasattr(cluster_cmp,
                                                           "network_id")
                         else cluster_cmp["network_id"],
                         "Invalid cluster network_id value")
        self.assertEqual(cluster_ref.name if hasattr(cluster_ref, "name")
                         else cluster_ref["name"],
                         cluster_cmp.name if hasattr(cluster_cmp, "name")
                         else cluster_cmp["name"],
                         "Invalid cluster name value")
        self.assertEqual(cluster_ref.status if hasattr(cluster_ref, "status")
                         else cluster_ref["status"],
                         cluster_cmp.status if hasattr(cluster_cmp, "status")
                         else cluster_cmp["status"],
                         "Invalid cluster status value")
        self.assertEqual(cluster_ref.flavor if hasattr(cluster_ref, "flavor")
                         else cluster_ref["flavor"],
                         cluster_cmp.flavor if hasattr(cluster_cmp, "flavor")
                         else cluster_cmp["flavor"],
                         "Invalid cluster flavor value")
        self.assertEqual(cluster_ref.size if hasattr(cluster_ref, "size")
                         else cluster_ref["size"],
                         cluster_cmp.size if hasattr(cluster_cmp, "size")
                         else cluster_cmp["size"],
                         "Invalid cluster size value")
        self.assertEqual(cluster_ref.volume_size if hasattr(cluster_ref,
                                                            "volume_size")
                         else cluster_ref["volume_size"],
                         cluster_cmp.volume_size if hasattr(cluster_cmp,
                                                            "volume_size")
                         else cluster_cmp["volume_size"],
                         "Invalid cluster volume_size value")

        self.compare_dates(cluster_ref.created_at if hasattr(cluster_ref,
                                                             "created_at")
                           else cluster_ref["created_at"],
                           cluster_cmp.created_at if hasattr(cluster_cmp,
                                                             "created_at")
                           else cluster_cmp["created_at"])

        self.compare_dates(cluster_ref.updated_at if hasattr(cluster_ref,
                                                             "updated_at")
                           else cluster_ref["updated_at"],
                           cluster_cmp.updated_at if hasattr(cluster_cmp,
                                                             "updated_at")
                           else cluster_cmp["updated_at"])

    def test_cluster_object_generation(self):
        """Test Cluster Object generation from a cluster dictionary object."""
        cluster_dict = test_utils.get_test_cluster()
        cluster_object = objects.Cluster(**cluster_dict)
        self.validate_cluster_values(cluster_object, cluster_dict)

    def test_node_object_generation(self):
        """Test Node Object generation from a cluster dictionary object."""

    def test_endpoint_object_generation(self):
        """Test Endpoint Object generation from a cluster dictionary object."""

    def test_cluster_api_to_object_to_api(self):
        """Tests Cluster api object conversion to Cluster object and back

        to api object.
        """
        api_cluster = test_utils.create_api_test_cluster_all()
        object_cluster = objects.Cluster(**api_cluster.as_dict())
        self.validate_cluster_values(api_cluster, object_cluster)
        api_cluster_2 = cluster.ClusterDetails(**object_cluster.as_dict())
        self.validate_cluster_values(api_cluster, api_cluster_2)

    def test_cluster_db_to_object_to_db(self):
        """Tests Cluster db object conversion to Cluster object and back

        to db object.
        """
        db_cluster_object = test_utils.create_db_test_cluster_model_object(
            self.context, deleted_at=timeutils.utcnow(), deleted=True)
        object_cluster = objects.Cluster._from_db_object(objects.Cluster(),
                                                         db_cluster_object)
        self.validate_cluster_values(db_cluster_object, object_cluster)
        self.assertEqual(db_cluster_object.deleted,
                        object_cluster.deleted,
                        "Invalid cluster deleted_at value")
        self.compare_dates(db_cluster_object.deleted_at
                           if hasattr(db_cluster_object, "deleted_at")
                           else db_cluster_object["deleted_at"],
                           object_cluster.deleted_at
                           if hasattr(object_cluster, "deleted_at")
                           else object_cluster["deleted_at"])

        cluster_changes = object_cluster.obj_get_changes()
        db_cluster_object_2 = models.Cluster()
        db_cluster_object_2.update(cluster_changes)
        self.validate_cluster_values(db_cluster_object, db_cluster_object_2)
        self.assertEqual(db_cluster_object.deleted,
                        db_cluster_object_2.deleted,
                        "Invalid cluster deleted_at value")
        self.compare_dates(db_cluster_object.deleted_at
                           if hasattr(db_cluster_object, "deleted_at")
                           else db_cluster_object["deleted_at"],
                           db_cluster_object_2.deleted_at
                           if hasattr(db_cluster_object_2, "deleted_at")
                           else db_cluster_object_2["deleted_at"])


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

    def test_get_cluster_by_id(self):
        """Tests get Cluster by id from Cluster objects API."""

    def test_get_cluster_by_id_forbidden(self):
        """Tests get Cluster by id from Cluster objects API."""
        api_cluster = test_utils.create_db_test_cluster_from_objects_api(
            self.context)
        tenant_b = self.get_context(tenant='b')

        with mock.patch.object(
            objects.Cluster.dbapi, 'get_cluster_by_id',
                return_value=api_cluster):
            with testtools.ExpectedException(exception.NotAuthorized):
                objects.Cluster.get_cluster_by_id(tenant_b, api_cluster.id)

        """Tests marking clusters for delete from Cluster objects API."""

    def test_update_cluster_deleting(self):
        """Tests marking clusters for delete from Cluster objects API."""
        api_cluster = test_utils.create_db_test_cluster_from_objects_api(
            self.context)
        tenant_b = self.get_context(tenant='b')

        with mock.patch.object(
            objects.Cluster.dbapi, 'get_cluster_by_id',
                return_value=api_cluster):
            with testtools.ExpectedException(exception.NotAuthorized):
                objects.Cluster.update_cluster_deleting(
                    tenant_b, api_cluster.id)


class NodeObjectsApiTests(base.TestCase):
    def test_get_nodes_by_cluster_id(self):
        """Tests get nodes by cluster id from Nodes objects API."""


class EndpointObjectsApiTests(base.TestCase):
    def test_get_endpoints_by_node_id(self):
        """Tests get endpoint objects by node id from Endpoint objects API."""
