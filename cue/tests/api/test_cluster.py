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
Tests for the API /cluster/ controller methods.
"""

import uuid

from cue.db.sqlalchemy import models
from cue import objects
from cue.tests.api import api_common
from cue.tests import utils as test_utils


class TestGetCluster(api_common.ApiCommon):
    def setUp(self):
        super(TestGetCluster, self).setUp()

    def test_get_cluster_not_found(self):
        """test get non-existing cluster."""
        data = self.get_json('/clusters/' + str(uuid.uuid4()),
                             expect_errors=True)

        self.assertEqual(404, data.status_code,
                         'Invalid status code value received.')
        self.assertEqual('404 Not Found', data.status,
                         'Invalid status value received.')
        self.assertIn('Cluster was not found',
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_get_cluster_invalid_uuid_format(self):
        """test get cluster with invalid id uuid format."""
        invalid_uuid = u"25c06c22.fadd.4c83-a515-974a29668ba9"
        data = self.get_json('/clusters/' + invalid_uuid, expect_errors=True)

        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')
        self.assertEqual('400 Bad Request', data.status,
                         'Invalid status value received.')
        self.assertIn('badly formed cluster_id UUID string',
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_get_cluster_invalid_uri(self):
        """test get cluster with invalid URI string.

        Example: get /clusters/<cluster_id>/invalid_resource
        """

    def test_get_cluster_valid_uri(self):
        """test get cluster with valid URI strings.

        Examples (with and without end forward slash):
        get /clusters/<cluster_id>
        get /clusters/<cluster_id>/
        """

    def test_get_cluster(self):
        """test get cluster on valid existing cluster."""
        cluster = test_utils.create_db_test_cluster_from_objects_api(
            name=self.cluster_name)
        data = self.get_json('/clusters/' + cluster.id)

        self.validate_cluster_values(cluster, data["cluster"])


class TestDeleteCluster(api_common.ApiCommon):
    def setUp(self):
        super(TestDeleteCluster, self).setUp()

    def test_delete_cluster_not_found(self):
        """test delete non-existing cluster."""
        data = self.delete('/clusters/' + str(uuid.uuid4()),
                           expect_errors=True)

        self.assertEqual(404, data.status_code,
                         'Invalid status code value received.')
        self.assertEqual('404 Not Found', data.status,
                         'Invalid status value received.')
        self.assertIn('Cluster was not found',
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_delete_cluster_invalid_uuid_format(self):
        """test delete cluster with invalid uuid format."""
        invalid_uuid = u"25c06c22.fadd.4c83-a515-974a29668ba9"
        data = self.delete('/clusters/' + invalid_uuid, expect_errors=True)

        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')
        self.assertEqual('400 Bad Request', data.status,
                         'Invalid status value received.')
        self.assertIn('badly formed cluster_id UUID string',
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_deleted_cluster_already_deleted(self):
        """test delete cluster that has already been deleted."""

    def test_delete_pending_cluster(self):
        """test delete cluster that is pending deletion."""

    def test_delete_cluster(self):
        """test delete cluster on valid existing cluster."""
        cluster = test_utils.create_db_test_cluster_from_objects_api(
            name=self.cluster_name)
        cluster_in_db = objects.Cluster.get_cluster_by_id(cluster.id)
        self.assertEqual(models.Status.BUILDING, cluster_in_db.status,
                         "Invalid cluster status value")
        self.delete('/clusters/' + cluster.id)

        cluster_in_db = objects.Cluster.get_cluster_by_id(cluster.id)
        cluster.status = models.Status.DELETING
        cluster.updated_at = cluster_in_db.created_at
        cluster.updated_at = cluster_in_db.updated_at

        data = self.get_json('/clusters/' + cluster.id)
        self.validate_cluster_values(cluster, data["cluster"])