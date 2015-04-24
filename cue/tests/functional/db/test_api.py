# Copyright 2014 Hewlett-Packard Development Company, L.P.
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


import uuid

from oslo_db import exception as oslo_exception

from cue.common import exception
from cue.db import api as db_api
from cue.tests.functional import base


UUID1 = str(uuid.uuid4())
UUID2 = str(uuid.uuid4())


class TestApi(base.FunctionalTestCase):

    dbapi = db_api.get_instance()

    def test_get_clusters(self):
        """Verifies get clusters DB API."""

    def test_create_clusters(self):
        """Verifies create cluster DB API."""
        cluster_values = {
            "project_id": UUID1,
            "name": "Rabbit Cluster",
            "network_id": UUID2,
            "flavor": "medium",
            "size": 5,
            "volume_size": 250,
        }

        db_cluster = self.dbapi.create_cluster(self.context, cluster_values)
        self.assertEqual(cluster_values["name"], db_cluster.name,
                         "invalid name value")
        self.assertEqual(cluster_values["network_id"], db_cluster.network_id,
                         "invalid network_id value")
        self.assertEqual(cluster_values["flavor"], db_cluster.flavor,
                         "invalid flavor value")
        self.assertEqual(cluster_values["size"], db_cluster.size,
                         "invalid size value")
        self.assertEqual(cluster_values["volume_size"], db_cluster.volume_size,
                         "invalid volume_size value")
        self.assertEqual(False, db_cluster.deleted, "invalid deleted value")

    def test_get_cluster_by_id(self):
        """Verifies create cluster DB API."""

    def test_get_nodes_in_cluster(self):
        """Verifies create cluster DB API."""
        cluster_values = {
            "project_id": UUID1,
            "name": "Rabbit Cluster",
            "network_id": UUID2,
            "flavor": "medium",
            "size": 5,
            "volume_size": 250,
        }

        db_cluster = self.dbapi.create_cluster(self.context, cluster_values)
        db_nodes = self.dbapi.get_nodes_in_cluster(self.context, db_cluster.id)

        for node in db_nodes:
            self.assertEqual(db_cluster.id, node.cluster_id,
                             "invalid flavor value")
            self.assertEqual(cluster_values["flavor"], node.flavor,
                             "invalid flavor value")
            self.assertEqual(False, node.deleted,
                             "invalid deleted value")

    def test_get_endpoints_in_node(self):
        """Verifies create cluster DB API."""

    def test_update_cluster_deleting(self):
        """Verifies create cluster DB API."""

    def test_create_broker(self):
        """Verifies create broker DB API."""

        broker_values = {
            "name": "Test Broker Name",
            "active": 1
        }

        db_broker = self.dbapi.create_broker(self.context, broker_values)

        self.assertEqual(broker_values['name'], db_broker.name,
                         "invalid broker name value")
        self.assertEqual(broker_values['active'], db_broker.active,
                         "invalid broker active value")

    def test_get_brokers(self):
        """Verifies get brokers DB API."""

        brokers = self.dbapi.get_brokers(self.context)
        self.assertIsNotNone(brokers,
                             "Should have found the default RabbitMQ broker.")
        self.assertIs(len(brokers),
                      1,
                      "Should have found only 1 broker, instead found " +
                      str(len(brokers)))
        self.assertEqual(brokers[0].name,
                         "rabbitmq",
                         "Should have found the default rabbitmq broker, "
                         "instead found: " + str(brokers[0].name))

    def test_delete_broker(self):
        """Verifies delete broker DB API."""

        brokers = self.dbapi.get_brokers(self.context)
        self.assertIs(len(brokers),
                      1,
                      "Should have found only 1 broker, instead found " +
                      str(len(brokers)))
        broker_id = brokers[0].id

        self.dbapi.delete_broker(self.context, broker_id)
        brokers = self.dbapi.get_brokers(self.context)
        self.assertIs(len(brokers),
                      0,
                      "Should have found 0 brokers after deleting the "
                      "default broker. Instead found " + str(len(brokers)))

    def test_update_broker(self):
        """Verifies update broker DB API."""

        brokers = self.dbapi.get_brokers(self.context)
        self.assertIs(len(brokers),
                      1,
                      "Should have found only 1 broker, instead found " +
                      str(len(brokers)))
        broker_id = brokers[0].id

        self.assertEqual(brokers[0].name,
                         "rabbitmq",
                         "Should have found the default rabbitmq broker.  "
                         "Instead found: " + brokers[0].name)

        broker_values = {
            "name": "Test Broker Name",
            "active": 1
        }

        self.dbapi.update_broker(self.context, broker_id, broker_values)

        brokers = self.dbapi.get_brokers(self.context)
        self.assertIs(len(brokers),
                      1, "Should have found only 1 broker, instead found " +
                      str(len(brokers)))

        self.assertEqual(brokers[0].name,
                         "Test Broker Name",
                         "Should have found the default rabbitmq broker.  "
                         "Instead found: " + brokers[0].name)

    def test_create_broker_metadata(self):
        """Verifies create broker metadata DB API."""

        broker_values = {
            "name": "Test Broker Name",
            "active": 1
        }

        db_broker = self.dbapi.create_broker(self.context, broker_values)
        broker_metadata_values = {
            "broker_id": db_broker.id,
            "key": "IMAGE",
            "value": "test_image"
        }
        db_broker = self.dbapi.create_broker_metadata(self.context,
                                                      broker_metadata_values)

        self.assertEqual(broker_metadata_values['broker_id'],
                         db_broker.broker_id,
                         "invalid broker_metadata ID")
        self.assertEqual(broker_metadata_values['key'], db_broker.key,
                         "invalid broker key")
        self.assertEqual(broker_metadata_values['value'], db_broker.value,
                         "invalid broker value")

        # Testing broker ID that should not exist in the table
        broker_metadata_values['broker_id'] = UUID1
        try:
            self.assertRaises(exception.NotFound,
                              self.dbapi.create_broker_metadata,
                              self.context,
                              broker_metadata_values)
        except Exception as err:
            self.assertIsNotNone(None,
                                 "Unhandled exception from "
                                 "create_broker_metadata with UUI that isn't "
                                 "in the broker table: " + str(err))

        # Testing with non-UUID formatted ID
        broker_metadata_values['broker_id'] = "Not a UUID"
        try:
            self.assertRaises(exception.Invalid,
                              self.dbapi.create_broker_metadata,
                              self.context,
                              broker_metadata_values)
        except Exception as err:
            self.assertIsNotNone(None,
                                 "Unhandled exception from "
                                 "create_broker_metadata with invalid UUID: "
                                 + str(err))

    def test_get_broker_metadata_by_broker_id(self):
        """Verifies get broker metadata by broker id DB API."""

        brokers = self.dbapi.get_brokers(self.context)
        self.assertIs(len(brokers),
                      1,
                      "Should have found only 1 broker, instead found " +
                      str(len(brokers)))
        broker_id = brokers[0].id
        broker_metadata = self.dbapi.get_broker_metadata_by_broker_id(
            self.context,
            broker_id)

        self.assertIs(len(broker_metadata),
                      1,
                      "Should have found the default rabbitmq broker ID.")

        # TODO(team) May want to have all cue.db.sqlalchemy.api.Connection
        # TODO(team) functions that take a broker_id assert it is of type UUID
        self.assertRaises(oslo_exception.DBError,
                          self.dbapi.get_broker_metadata_by_broker_id,
                          self.context,
                          "Bad ID")

    def test_delete_broker_metadata(self):
        """Verifies delete broker metadata DB API."""

        brokers = self.dbapi.get_brokers(self.context)
        self.assertIs(len(brokers),
                      1,
                      "Should have found only 1 broker, instead found " +
                      str(len(brokers)))
        broker_id = brokers[0].id
        broker_metadata = self.dbapi.get_broker_metadata_by_broker_id(
            self.context,
            broker_id)

        self.dbapi.delete_broker_metadata(self.context, broker_metadata[0].id)

        broker_metadata = self.dbapi.get_broker_metadata_by_broker_id(
            self.context,
            broker_id)

        self.assertIs(0, len(broker_metadata), "Broker metadata should be "
                                               "empty after the delete.")

    def test_get_image_id_by_broker_name(self):

        default_metadata_id = "f7e8c49b-7d1e-472f-a78b-7c46a39c85be"
        image_id = self.dbapi.get_image_id_by_broker_name(self.context,
                                                          'rabbitmq')

        self.assertEqual(default_metadata_id, image_id,
                      "Should have found the image ID of the default rabbitmq"
                      " broker.")