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

from cue.db import api as db_api
from cue.tests import base


UUID1 = str(uuid.uuid4())
UUID2 = str(uuid.uuid4())


class ApiTests(base.TestCase):

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

        db_cluster = self.dbapi.create_cluster(cluster_values)
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

        db_cluster = self.dbapi.create_cluster(cluster_values)
        db_nodes = self.dbapi.get_nodes_in_cluster(db_cluster.id)

        for node in db_nodes:
            self.assertEqual(db_cluster.id, node.cluster_id,
                             "invalid flavor value")
            self.assertEqual(cluster_values["flavor"], node.flavor,
                             "invalid flavor value")
            self.assertEqual(cluster_values["volume_size"],
                             node.volume_size,
                             "invalid volume_size value")
            self.assertEqual(False, node.deleted,
                             "invalid deleted value")

    def test_get_endpoints_in_node(self):
        """Verifies create cluster DB API."""

    def test_mark_cluster_as_delete(self):
        """Verifies create cluster DB API."""