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
from cue.tests import api
from cue.tests.api import api_utils
from cue.tests import utils as test_utils

from oslo.config import cfg

CONF = cfg.CONF


class TestListClusters(api.FunctionalTest,
                       api_utils.ClusterValidationMixin):
    def setUp(self):
        super(TestListClusters, self).setUp()

    def test_empty(self):
        data = self.get_json('/clusters')
        self.assertEqual([], data["clusters"])

    def test_one(self):
        cluster = test_utils.create_db_test_cluster_from_objects_api(
            self.context,
            name=self.cluster_name)
        data = self.get_json('/clusters', headers=self.auth_headers)
        # verify number of clusters received
        self.assertEqual(len(data), 1, "Invalid number of clusters returned")
        # verify cluster
        self.validate_cluster_values(cluster, data["clusters"][0])
        # verify endpoints in cluster
        all_endpoints = test_utils.get_endpoints_in_cluster(self.context,
                                                            cluster.id)
        self.validate_endpoint_values(all_endpoints,
                                      data["clusters"][0]["end_points"])

    def test_multiple(self):
        num_of_clusters = 5
        clusters = [test_utils.create_db_test_cluster_from_objects_api(
            self.context,
            name=self.cluster_name + '_' + str(i), size=i + 1) for i in
                    range(num_of_clusters)]

        data = self.get_json('/clusters', headers=self.auth_headers)
        # verify number of clusters received
        self.assertEqual(len(data["clusters"]), num_of_clusters,
                         "Invalid number of clusters returned")
        for i in range(num_of_clusters):
            # verify cluster
            self.validate_cluster_values(clusters[i], data["clusters"][i])
            # verify endpoints in cluster
            all_endpoints = test_utils.get_endpoints_in_cluster(self.context,
                                                                clusters[i].id)
            self.validate_endpoint_values(all_endpoints,
                                          data["clusters"][i]["end_points"])


class TestCreateCluster(api.FunctionalTest,
                        api_utils.ClusterValidationMixin):

    def setUp(self):
        super(TestCreateCluster, self).setUp()

    def test_create_empty_body(self):
        cluster_params = {}
        #header = {'Content-Type': 'application/json'}
        data = self.post_json('/clusters', params=cluster_params,
                              expect_errors=True)
        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')
        self.assertEqual('400 Bad Request', data.status,
                         'Invalid status value received.')
        self.assertIn('Invalid input for field/attribute',
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_create_size_missing(self):
        """test create an empty cluster."""
        api_cluster = test_utils.create_api_test_cluster(size=0)
        request_body = api_cluster.as_dict()

        # remove size field
        del request_body['size']

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=request_body,
                            expect_errors=True)
        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')
        self.assertEqual('400 Bad Request', data.status,
                         'Invalid status value received.')
        self.assertIn('Mandatory field missing',
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_create_size_zero(self):
        """test create an empty cluster."""
        api_cluster = test_utils.create_api_test_cluster(size=0)

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster.as_dict(),
                            expect_errors=True)
        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')
        self.assertEqual('400 Bad Request', data.status,
                         'Invalid status value received.')
        self.assertIn('Invalid cluster size provided',
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_create_too_large(self):
        """test create cluster with size larger than limit."""
        api_cluster = test_utils.create_api_test_cluster(
            size=(CONF.api.max_cluster_size + 1))

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster.as_dict(),
                            expect_errors=True)
        self.assertEqual(413, data.status_code,
                         'Invalid status code value received.')
        self.assertIn('Invalid cluster size, max size is: ' +
                      str(CONF.api.max_cluster_size),
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_create_size_one(self):
        """test create a cluster with one node.

        Will verify cluster create from DB record then verifies cluster get
        returns the same cluster from the API.
        """
        api_cluster = test_utils.create_api_test_cluster(size=1)
        data = self.post_json('/clusters', params=api_cluster.as_dict(),
                              headers=self.auth_headers, status=202)
        cluster = objects.Cluster.get_cluster_by_id(self.context,
                                                    data.json["cluster"]["id"])
        self.validate_cluster_values(cluster, data.json["cluster"])
        self.assertEqual(models.Status.BUILDING,
                         data.json["cluster"]['status'])

        data_api = self.get_json('/clusters/' + cluster.id,
                                 headers=self.auth_headers)
        self.validate_cluster_values(cluster, data_api["cluster"])
        self.assertEqual(models.Status.BUILDING, data_api["cluster"]['status'])

    def test_create_size_three(self):
        """test create a cluster with three nodes.

        Will verify cluster create from DB record then verifies cluster get
        returns the same cluster from the API.
        """
        api_cluster = test_utils.create_api_test_cluster(size=3)
        data = self.post_json('/clusters', params=api_cluster.as_dict(),
                              headers=self.auth_headers, status=202)
        cluster = objects.Cluster.get_cluster_by_id(self.context,
                                                    data.json["cluster"]["id"])
        self.validate_cluster_values(cluster, data.json["cluster"])
        self.assertEqual(models.Status.BUILDING,
                         data.json["cluster"]['status'])

        data_api = self.get_json('/clusters/' + cluster.id,
                                 headers=self.auth_headers)
        self.validate_cluster_values(cluster, data_api["cluster"])
        self.assertEqual(models.Status.BUILDING, data_api["cluster"]['status'])

    def test_create_invalid_size_format(self):
        """test with invalid formatted size parameter."""
        api_cluster = test_utils.create_api_test_cluster(size="a")

        data = self.post_json('/clusters', params=api_cluster.as_dict(),
                              headers=self.auth_headers, expect_errors=True)
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
