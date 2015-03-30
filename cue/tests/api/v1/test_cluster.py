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
from cue.tests import api
from cue.tests.api import api_utils
from cue.tests import utils as test_utils

from oslo.config import cfg

CONF = cfg.CONF


class TestGetCluster(api.FunctionalTest, api_utils.ClusterValidationMixin):
    def setUp(self):
        super(TestGetCluster, self).setUp()

    def test_get_cluster_not_found(self):
        """test get non-existing cluster."""
        data = self.get_json('/clusters/' + str(uuid.uuid4()),
                             headers=self.auth_headers, expect_errors=True)

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
        data = self.get_json('/clusters/' + invalid_uuid,
                             headers=self.auth_headers, expect_errors=True)

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
        # create record for a new cluster in db
        cluster = test_utils.create_db_test_cluster_from_objects_api(
            self.context, name=self.cluster_name, size=3).as_dict()
        data = self.get_json('/clusters/' + cluster['id'],
                             headers=self.auth_headers)

        self.validate_cluster_values(cluster, data)

        # verify all endpoints in cluster
        all_endpoints = test_utils.get_endpoints_in_cluster(self.context,
                                                            cluster['id'])
        self.validate_endpoint_values(all_endpoints, data["end_points"])


class TestDeleteCluster(api.FunctionalTest, api_utils.ClusterValidationMixin):
    def setUp(self):
        super(TestDeleteCluster, self).setUp()

    def test_delete_cluster_not_found(self):
        """test delete non-existing cluster."""
        data = self.delete('/clusters/' + str(uuid.uuid4()),
                           headers=self.auth_headers, expect_errors=True)

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
        data = self.delete('/clusters/' + invalid_uuid,
                           headers=self.auth_headers, expect_errors=True)

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
            self.context, name=self.cluster_name)
        cluster_in_db = objects.Cluster.get_cluster_by_id(self.context,
                                                          cluster.id)
        self.assertEqual(models.Status.BUILDING, cluster_in_db.status,
                         "Invalid cluster status value")

        self.delete('/clusters/' + cluster.id, headers=self.auth_headers)
        cluster_in_db = objects.Cluster.get_cluster_by_id(self.context,
                                                          cluster.id)
        cluster.status = models.Status.DELETING
        cluster.updated_at = cluster_in_db.created_at
        cluster.updated_at = cluster_in_db.updated_at

        data = self.get_json('/clusters/' + cluster['id'],
                             headers=self.auth_headers)

        self.validate_cluster_values(cluster.as_dict(), data)


class TestListClusters(api.FunctionalTest, api_utils.ClusterValidationMixin):
    def setUp(self):
        super(TestListClusters, self).setUp()

    def test_empty(self):
        data = self.get_json('/clusters')
        self.assertEqual([], data)

    def test_one(self):
        cluster = test_utils.create_db_test_cluster_from_objects_api(
            self.context, name=self.cluster_name)
        data = self.get_json('/clusters', headers=self.auth_headers)
        # verify number of clusters received
        self.assertEqual(len(data), 1, "Invalid number of clusters returned")
        # verify cluster
        self.validate_cluster_values(cluster.as_dict(), data[0])
        # verify endpoints in cluster
        all_endpoints = test_utils.get_endpoints_in_cluster(self.context,
                                                            cluster.id)
        self.validate_endpoint_values(all_endpoints,
                                            data[0]["end_points"])

    def test_multiple(self):
        num_of_clusters = 5
        clusters = [test_utils.create_db_test_cluster_from_objects_api(
            self.context,
            name=self.cluster_name + '_' + str(i), size=i + 1) for i in
                     range(num_of_clusters)]

        data = self.get_json('/clusters', headers=self.auth_headers)
        # verify number of clusters received
        self.assertEqual(len(data), num_of_clusters,
                         "Invalid number of clusters returned")
        for i in range(num_of_clusters):
            # verify cluster
            self.validate_cluster_values(clusters[i].as_dict(), data[i])
            # verify endpoints in cluster
            all_endpoints = test_utils.get_endpoints_in_cluster(self.context,
                                                                clusters[i].id)
            self.validate_endpoint_values(all_endpoints,
                                                data[i]["end_points"])


class TestCreateCluster(api.FunctionalTest, api_utils.ClusterValidationMixin):
    def setUp(self):
        super(TestCreateCluster, self).setUp()

    def test_create_empty_body(self):
        cluster_params = {}
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
                              params=request_body, expect_errors=True)
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
                              params=api_cluster.as_dict(), expect_errors=True)
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
                                                    data.json["id"]).as_dict()
        self.validate_cluster_values(cluster, data.json)
        self.assertEqual(models.Status.BUILDING, data.json['status'])

        data_api = self.get_json('/clusters/' + cluster['id'],
                                 headers=self.auth_headers)
        self.validate_cluster_values(cluster, data_api)
        self.assertEqual(models.Status.BUILDING, data_api['status'])

    def test_create_size_three(self):
        """test create a cluster with three nodes.

        Will verify cluster create from DB record then verifies cluster get
        returns the same cluster from the API.
        """
        api_cluster = test_utils.create_api_test_cluster(size=3)
        data = self.post_json('/clusters', params=api_cluster.as_dict(),
                              headers=self.auth_headers, status=202)

        cluster = objects.Cluster.get_cluster_by_id(self.context,
                                                    data.json["id"]).as_dict()
        self.validate_cluster_values(cluster, data.json)
        self.assertEqual(models.Status.BUILDING, data.json['status'])

        data_api = self.get_json('/clusters/' + cluster['id'],
                                 headers=self.auth_headers)
        self.validate_cluster_values(cluster, data_api)
        self.assertEqual(models.Status.BUILDING, data_api['status'])

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

    def test_create_network_id_size_not_one(self):
        """test create a cluster with size of network_id more than one."""
        api_cluster = test_utils.create_api_test_cluster(network_id=(
            [{"uuid": str(uuid.uuid4())}, {"uuid": str(uuid.uuid4())}]))

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster.as_dict(), expect_errors=True)
        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')
        self.assertIn("Invalid number of network_id's provided",
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
