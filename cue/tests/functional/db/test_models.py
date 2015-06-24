#    Copyright 2014 Rackspace
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
#
# Copied from Octavia
import uuid

from cue.db import api as db_api
from cue.db.sqlalchemy import api as sql_api
from cue.db.sqlalchemy import models
from cue.tests.functional import base

from oslo_utils import timeutils


UUID1 = str(uuid.uuid4())
UUID2 = str(uuid.uuid4())
UUID3 = str(uuid.uuid4())


class ModelsTests(base.FunctionalTestCase):

    def test_create_cluster_model(self):
        """Verifies a new cluster record is created in DB."""

        cluster_values = {
            "id": UUID1,
            "network_id": UUID3,
            "project_id": self.context.project_id,
            "name": "Cluster test",
            "status": models.Status.BUILDING,
            "flavor": "medium",
            "size": 3,
            "volume_size": 250,
            "deleted": False,
            "created_at": timeutils.utcnow(),
            "updated_at": timeutils.utcnow(),
            "deleted_at": timeutils.utcnow(),
        }

        cluster = models.Cluster()
        cluster.update(cluster_values)

        self.assertEqual(cluster_values["id"], cluster.id, "Invalid ID value")
        self.assertEqual(cluster_values["project_id"], cluster.project_id,
                         "Invalid project_id value")
        self.assertEqual(cluster_values["network_id"], cluster.network_id,
                         "Invalid network_id value")
        self.assertEqual(cluster_values["name"], cluster.name, "Invalid name"
                                                               "value")
        self.assertEqual(cluster_values["status"], cluster.status, "Invalid "
                                                                   "status"
                                                                   "value")
        self.assertEqual(cluster_values["flavor"], cluster.flavor,
                         "Invalid flavor value")
        self.assertEqual(cluster_values["size"], cluster.size,
                         "Invalid size value")
        self.assertEqual(cluster_values["volume_size"], cluster.volume_size,
                         "Invalid volume_size value")
        self.assertEqual(cluster_values["deleted"], cluster.deleted,
                         "Invalid deleted value")
        self.assertEqual(cluster_values["created_at"], cluster.created_at,
                         "Invalid created_at value")
        self.assertEqual(cluster_values["updated_at"], cluster.updated_at,
                         "Invalid updated_at value")
        self.assertEqual(cluster_values["deleted_at"], cluster.deleted_at,
                         "Invalid deleted_at value")

        db_session = sql_api.get_session()
        cluster.save(db_session)

        dbapi = db_api.get_instance()
        cluster_db = dbapi.get_cluster_by_id(self.context,
                                             cluster_values["id"])

        self.assertEqual(cluster_values["id"], cluster_db.id, "Invalid ID "
                                                              "value")
        self.assertEqual(cluster_values["project_id"], cluster_db.project_id,
                         "Invalid project_id value")
        self.assertEqual(cluster_values["network_id"], cluster_db.network_id,
                         "Invalid network_id value")
        self.assertEqual(cluster_values["name"], cluster_db.name, "Invalid "
                                                                  "name value")
        self.assertEqual(cluster_values["status"], cluster_db.status,
                         "Invalid status value")
        self.assertEqual(cluster_values["flavor"], cluster_db.flavor,
                         "Invalid flavor value")
        self.assertEqual(cluster_values["size"], cluster_db.size,
                         "Invalid size value")
        self.assertEqual(cluster_values["volume_size"], cluster_db.volume_size,
                         "Invalid volume_size value")
        self.assertEqual(cluster_values["deleted"], cluster_db.deleted,
                         "Invalid deleted value")
        self.assertEqual(cluster_values["created_at"], cluster_db.created_at,
                         "Invalid created_at value")
        self.assertEqual(cluster_values["updated_at"], cluster_db.updated_at,
                         "Invalid updated_at value")
        self.assertEqual(cluster_values["deleted_at"], cluster_db.deleted_at,
                         "Invalid deleted_at value")

    def test_create_node_model(self):
        """Verifies a new cluster record is created in DB."""

        dbapi = db_api.get_instance()
        cluster_values = {
            "network_id": UUID3,
            "project_id": UUID2,
            "name": "Cluster test",
            "flavor": "medium",
            "size": 3,
            "volume_size": 250,
        }
        db_cluster = dbapi.create_cluster(self.context, cluster_values)

        node_values = {
            "id": UUID1,
            "cluster_id": db_cluster.id,
            "instance_id": "NovaInstanceId",
            "flavor": "Large",
            "status": models.Status.BUILDING,
            "deleted": False,
            "created_at": timeutils.utcnow(),
            "updated_at": timeutils.utcnow(),
            "deleted_at": timeutils.utcnow(),
        }

        node = models.Node()
        node.update(node_values)

        self.assertEqual(node_values["id"], node.id, "Invalid ID value")
        self.assertEqual(node_values["cluster_id"], node.cluster_id,
                         "Invalid cluster_id value")
        self.assertEqual(node_values["instance_id"], node.instance_id,
                         "Invalid instance_id value")
        self.assertEqual(node_values["status"], node.status, "Invalid status "
                                                             "value")
        self.assertEqual(node_values["flavor"], node.flavor, "Invalid flavor "
                                                             "value")
        self.assertEqual(node_values["deleted"], node.deleted,
                         "Invalid deleted value")
        self.assertEqual(node_values["created_at"], node.created_at,
                         "Invalid created_at value")
        self.assertEqual(node_values["updated_at"], node.updated_at,
                         "Invalid updated_at value")
        self.assertEqual(node_values["deleted_at"], node.deleted_at,
                         "Invalid deleted_at value")

        db_session = sql_api.get_session()
        node.save(db_session)

        node_db = dbapi.get_node_by_id(self.context, node_values["id"])

        self.assertEqual(node_values["id"], node_db.id, "Invalid ID value")
        self.assertEqual(node_values["cluster_id"], node_db.cluster_id,
                         "Invalid cluster_id value")
        self.assertEqual(node_values["instance_id"], node_db.instance_id,
                         "Invalid instance_id value")
        self.assertEqual(node_values["status"], node_db.status, "Invalid "
                                                                "status value")
        self.assertEqual(node_values["flavor"], node_db.flavor, "Invalid "
                                                                "flavor value")
        self.assertEqual(node_values["deleted"], node_db.deleted,
                         "Invalid deleted value")
        self.assertEqual(node_values["created_at"], node_db.created_at,
                         "Invalid created_at value")
        self.assertEqual(node_values["updated_at"], node_db.updated_at,
                         "Invalid updated_at value")
        self.assertEqual(node_values["deleted_at"], node_db.deleted_at,
                         "Invalid deleted_at value")

    def test_create_endpoint_model(self):
        """Verifies a new cluster record is created in DB."""

        dbapi = db_api.get_instance()
        cluster_values = {
            "network_id": UUID3,
            "project_id": UUID2,
            "name": "Cluster test",
            "flavor": "medium",
            "size": 3,
            "volume_size": 250,
        }
        db_cluster = dbapi.create_cluster(self.context, cluster_values)

        node_values = {
            "cluster_id": db_cluster.id,
            "flavor": "Large",
            "status": models.Status.BUILDING,
        }

        node = models.Node()
        node.update(node_values)
        db_session = sql_api.get_session()
        node.save(db_session)

        endpoint_values = {
            "id": UUID1,
            "node_id": node.id,
            "uri": "amqp://10.20.30.40:10000",
            "type": "AMQP",
            "deleted": False,
        }

        endpoint = models.Endpoint()
        endpoint.update(endpoint_values)

        self.assertEqual(endpoint_values["id"], endpoint.id, "Invalid ID "
                                                             "value")
        self.assertEqual(endpoint_values["node_id"], endpoint.node_id,
                         "Invalid node_id value")
        self.assertEqual(endpoint_values["uri"], endpoint.uri, "Invalid uri"
                                                               "value")
        self.assertEqual(endpoint_values["type"], endpoint.type, "Invalid "
                                                                 "type"
                                                                 "value")
        self.assertEqual(endpoint_values["deleted"], endpoint.deleted,
                         "Invalid deleted value")

        endpoint.save(db_session)
        endpoint_db = dbapi.get_endpoint_by_id(self.context,
                                               endpoint_values["id"])

        self.assertEqual(endpoint_values["id"], endpoint_db.id, "Invalid ID "
                                                                "value")
        self.assertEqual(endpoint_values["node_id"], endpoint_db.node_id,
                         "Invalid node_id value")
        self.assertEqual(endpoint_values["uri"], endpoint_db.uri, "Invalid uri"
                                                                  "value")
        self.assertEqual(endpoint_values["type"], endpoint_db.type, "Invalid "
                                                                    "type"
                                                                    "value")
        self.assertEqual(endpoint_values["deleted"], endpoint_db.deleted,
                         "Invalid deleted value")