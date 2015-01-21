# -*- encoding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
Tests for the API /clusters/ controller methods.
"""
from cue.db.sqlalchemy import models
from cue import objects
from cue.tests.api import api_common
from cue.tests import utils as test_utils


class TestListClusters(api_common.ApiCommon):
    def setUp(self):
        super(TestListClusters, self).setUp()

    def test_empty(self):
        data = self.get_json('/clusters')
        self.assertEqual([], data["clusters"])

    def test_one(self):
        cluster = test_utils.create_db_test_cluster_from_objects_api(
            name=self.cluster_name)
        data = self.get_json('/clusters')

        self.assertEqual(len(data), 1, "Invalid number of clusters returned")

        self.validate_cluster_values(cluster, data["clusters"][0])

    def test_multiple(self):
        cluster_0 = test_utils.create_db_test_cluster_from_objects_api(
            name=self.cluster_name + '_0')
        cluster_1 = test_utils.create_db_test_cluster_from_objects_api(
            name=self.cluster_name + '_1')
        cluster_2 = test_utils.create_db_test_cluster_from_objects_api(
            name=self.cluster_name + '_2')
        cluster_3 = test_utils.create_db_test_cluster_from_objects_api(
            name=self.cluster_name + '_3')
        cluster_4 = test_utils.create_db_test_cluster_from_objects_api(
            name=self.cluster_name + '_4')

        data = self.get_json('/clusters')

        self.assertEqual(len(data["clusters"]), 5, "Invalid number of clusters"
                                                   " returned")

        self.validate_cluster_values(cluster_0, data["clusters"][0])
        self.validate_cluster_values(cluster_1, data["clusters"][1])
        self.validate_cluster_values(cluster_2, data["clusters"][2])
        self.validate_cluster_values(cluster_3, data["clusters"][3])
        self.validate_cluster_values(cluster_4, data["clusters"][4])


class TestCreateCluster(api_common.ApiCommon):
    def setUp(self):
        super(TestCreateCluster, self).setUp()

    def test_create_empty_body(self):
        cluster_params = {}
        header = {'Content-Type': 'application/json'}
        data = self.post_json('/clusters', params=cluster_params,
                              headers=header, expect_errors=True)
        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')
        self.assertEqual('400 Bad Request', data.status,
                         'Invalid status value received.')
        self.assertIn('Invalid input for field/attribute',
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_create_size_zero(self):
        """test create an empty cluster."""
        api_cluster = test_utils.create_api_test_cluster(size=0)
        header = {'Content-Type': 'application/json'}
        data = self.post_json('/clusters', params=api_cluster.as_dict(),
                              headers=header, expect_errors=True)
        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')
        self.assertEqual('400 Bad Request', data.status,
                         'Invalid status value received.')
        self.assertIn('Invalid cluster size provided',
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_create_size_one(self):
        """test create a cluster with one node.

        Will verify cluster create from DB record then verifies cluster get
        returns the same cluster from the API.
        """
        api_cluster = test_utils.create_api_test_cluster(size=1)
        header = {'Content-Type': 'application/json'}
        data = self.post_json('/clusters', params=api_cluster.as_dict(),
                              headers=header, status=202)
        cluster = objects.Cluster.get_cluster_by_id(data.json["cluster"]["id"])
        self.validate_cluster_values(cluster, data.json["cluster"])
        self.assertEqual(models.Status.BUILDING,
                         data.json["cluster"]['status'])

        data_api = self.get_json('/clusters/' + cluster.id)
        self.validate_cluster_values(cluster, data_api["cluster"])
        self.assertEqual(models.Status.BUILDING, data_api["cluster"]['status'])

    def test_create_size_three(self):
        """test create a cluster with three nodes.

        Will verify cluster create from DB record then verifies cluster get
        returns the same cluster from the API.
        """
        api_cluster = test_utils.create_api_test_cluster(size=3)
        header = {'Content-Type': 'application/json'}
        data = self.post_json('/clusters', params=api_cluster.as_dict(),
                              headers=header, status=202)
        cluster = objects.Cluster.get_cluster_by_id(data.json["cluster"]["id"])
        self.validate_cluster_values(cluster, data.json["cluster"])
        self.assertEqual(models.Status.BUILDING,
                         data.json["cluster"]['status'])

        data_api = self.get_json('/clusters/' + cluster.id)
        self.validate_cluster_values(cluster, data_api["cluster"])
        self.assertEqual(models.Status.BUILDING, data_api["cluster"]['status'])

    def test_create_invalid_size_format(self):
        """test with invalid formatted size parameter."""
        api_cluster = test_utils.create_api_test_cluster(size="a")
        header = {'Content-Type': 'application/json'}
        data = self.post_json('/clusters', params=api_cluster.as_dict(),
                              headers=header, expect_errors=True)
        self.assertEqual(500, data.status_code,
                         'Invalid status code value received.')
        self.assertEqual('500 Internal Server Error', data.status,
                         'Invalid status value received.')
        self.assertIn('invalid literal for int() with base 10:',
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_create_invalid_volume_size(self):
        """test with invalid volume_size parameter."""

    def test_create_invalid_parameter_set_id(self):
        """test with invalid parameter set: id."""

    def test_create_invalid_parameter_set_status(self):
        """test with invalid parameter set: status."""

    def test_create_invalid_parameter_set_created_at(self):
        """test with invalid parameter set: created_at."""

    def test_create_invalid_parameter_set_updated_at(self):
        """test with invalid parameter set: updated_at."""

    def test_create_invalid_parameter_set_deleted_at(self):
        """test with invalid parameter set: deleted_at."""
