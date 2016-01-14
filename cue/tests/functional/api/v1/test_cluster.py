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

from cue.common import validate_auth_token as auth_validate
from cue.db.sqlalchemy import api as db_api
from cue.db.sqlalchemy import models
from cue import objects
from cue.tests.functional import api
from cue.tests.functional.api import api_utils
from cue.tests.functional import utils as test_utils


class TestGetCluster(api.APITest,
                     api_utils.ClusterValidationMixin):

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
        self.assertIn('Invalid cluster ID format provided',
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
        self.validate_endpoint_values(all_endpoints, data["endpoints"])


class TestDeleteCluster(api.APITest,
                        api_utils.ClusterValidationMixin):

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
        self.assertIn('Invalid cluster ID format provided',
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
        cluster.created_at = cluster_in_db.created_at
        cluster.updated_at = cluster_in_db.updated_at

        data = self.get_json('/clusters/' + cluster['id'],
                             headers=self.auth_headers)
        cluster = cluster.as_dict()
        self.validate_cluster_values(cluster, data)


class TestListClusters(api.APITest,
                       api_utils.ClusterValidationMixin):

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
                                            data[0]["endpoints"])

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
                                                data[i]["endpoints"])


class TestCreateCluster(api.APITest,
                        api_utils.ClusterValidationMixin):
    def setUp(self):
        super(TestCreateCluster, self).setUp()

    def test_create_empty_body(self):
        """test create cluster with empty request body."""
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
        request_body = api_cluster

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
                              params=api_cluster,
                            expect_errors=True)
        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')
        self.assertEqual('400 Bad Request', data.status,
                         'Invalid status value received.')
        self.assertIn('Invalid cluster size provided',
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_create_too_large(self):
        """test create cluster with size greater than limit."""
        max_cluster_size = 3
        self.CONF.config(max_cluster_size=max_cluster_size, group='api')
        """test create cluster with size larger than limit."""
        api_cluster = test_utils.create_api_test_cluster(
            size=(max_cluster_size + 1))

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster, expect_errors=True)
        self.assertEqual(413, data.status_code,
                         'Invalid status code value received.')
        self.assertIn('Invalid cluster size, max size is: ' +
                      str(max_cluster_size),
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_create_size_one(self):
        """test create a cluster with one node.

        Will verify cluster create from DB record then verifies cluster get
        returns the same cluster from the API.
        """
        api_cluster = test_utils.create_api_test_cluster(size=1)
        data = self.post_json('/clusters', params=api_cluster,
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
        data = self.post_json('/clusters', params=api_cluster,
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

        data = self.post_json('/clusters', params=api_cluster,
                              headers=self.auth_headers, expect_errors=True)
        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')
        self.assertEqual('400 Bad Request', data.status,
                         'Invalid status value received.')
        self.assertIn('invalid literal for int() with base 10:',
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_create_network_id_size_not_one(self):
        """test create a cluster with size of network_id more than one."""
        api_cluster = test_utils.create_api_test_cluster(network_id=(
                        [str(uuid.uuid4()), str(uuid.uuid4())]))

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster, expect_errors=True)
        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')
        self.assertIn("Invalid number of network_id's",
                      data.namespace["faultstring"],
                      'Invalid faultstring received.')

    def test_create_two_clusters_verify_time_stamps(self):
        """test time stamps times at creation and delete."""
        api_cluster_1 = test_utils.create_api_test_cluster()
        api_cluster_2 = test_utils.create_api_test_cluster()

        # Create two clusters
        data_1 = self.post_json('/clusters', params=api_cluster_1,
                              headers=self.auth_headers, status=202)
        data_2 = self.post_json('/clusters', params=api_cluster_2,
                              headers=self.auth_headers, status=202)

        # retrieve cluster objects
        cluster_1 = objects.Cluster.get_cluster_by_id(self.context,
                                                      data_1.json["id"])
        cluster_2 = objects.Cluster.get_cluster_by_id(self.context,
                                                      data_2.json["id"])

        # verify second cluster was created after first by created_at time
        self.assertTrue(cluster_2.created_at > cluster_1.created_at,
                         "Second cluster was not created after first")

        cluster_1_created_at = cluster_1.created_at

        # issue delete request cluster for cluster_1
        self.delete('/clusters/' + data_1.json["id"],
                    headers=self.auth_headers)

        # retrieve cluster_1
        cluster_1 = objects.Cluster.get_cluster_by_id(self.context,
                                                      data_1.json["id"])

        # verify updated_at time is after created_at
        self.assertTrue(cluster_1.updated_at > cluster_1.created_at,
                         "Cluster updated at time is invalid")
        # verify created_at time did not change
        self.assertEqual(cluster_1_created_at, cluster_1.created_at,
                         "Cluster created_at time has changed")

        # delete cluster_1
        cluster = objects.Cluster(deleted=True, status=models.Status.DELETED)
        cluster.update(self.context, data_1.json["id"])

        # retrieve deleted (soft) cluster
        cluster_query = db_api.model_query(self.context, models.Cluster,
                                           read_deleted=True).filter_by(
            id=data_1.json["id"])
        cluster_1 = cluster_query.one()

        # verify deleted_at time is after created_at
        self.assertTrue(cluster_1.deleted_at > cluster_1.created_at,
                         "Cluster deleted_at time is invalid")
        # verify updated_at time is after deleted_at
        self.assertTrue(cluster_1.updated_at > cluster_1.deleted_at,
                         "Cluster deleted_at time is invalid")

    def test_create_rabbit_authentication_missing(self):
        """test create a cluster with missing authentication field."""
        api_cluster = test_utils.create_api_test_cluster()
        del api_cluster['authentication']

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster, expect_errors=True)

        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')

    def test_create_rabbit_authentication_token_missing(self):
        """test create a cluster with missing authentication token."""
        api_cluster = test_utils.create_api_test_cluster()
        del api_cluster['authentication']['token']

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster, expect_errors=True)

        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')

    def test_create_rabbit_authentication_type_missing(self):
        """test create a cluster with missing authentication type."""
        api_cluster = test_utils.create_api_test_cluster()
        del api_cluster['authentication']['type']

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster, expect_errors=True)

        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')

    def test_create_rabbit_authentication_username_missing(self):
        """test create a cluster with missing authentication username."""
        api_cluster = test_utils.create_api_test_cluster()
        del api_cluster['authentication']['token']['username']

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster, expect_errors=True)

        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')

    def test_create_rabbit_authentication_password_missing(self):
        """test create a cluster with missing authentication password."""
        api_cluster = test_utils.create_api_test_cluster()
        del api_cluster['authentication']['token']['password']

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster, expect_errors=True)

        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')

    def test_create_rabbit_authentication_invalid_type(self):
        """test create a cluster with invalid authentication type."""
        api_cluster = test_utils.create_api_test_cluster()
        api_cluster['authentication']['type'] = 'blah'

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster, expect_errors=True)

        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')

    def test_create_rabbit_authentication_too_short_username(self):
        """test create a cluster with invalid authentication username."""
        api_cluster = test_utils.create_api_test_cluster()
        api_cluster['authentication']['token']['username'] = ''

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster, expect_errors=True)

        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')

    def test_create_rabbit_authentication_too_short_password(self):
        """test create a cluster with invalid authentication password."""
        api_cluster = test_utils.create_api_test_cluster()
        api_cluster['authentication']['token']['password'] = ''

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster, expect_errors=True)

        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')

    def test_create_rabbit_authentication_too_long_username(self):
        """test create a cluster with invalid authentication username."""
        m = auth_validate.MAX_USERNAME_LENGTH + 1
        api_cluster = test_utils.create_api_test_cluster()
        api_cluster['authentication']['token']['username'] = 'x' * m

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster, expect_errors=True)

        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')

    def test_create_rabbit_authentication_too_long_password(self):
        """test create a cluster with invalid authentication password."""
        m = auth_validate.MAX_PASSWORD_LENGTH + 1
        api_cluster = test_utils.create_api_test_cluster()
        api_cluster['authentication']['token']['password'] = 'y' * m

        data = self.post_json('/clusters', headers=self.auth_headers,
                              params=api_cluster, expect_errors=True)

        self.assertEqual(400, data.status_code,
                         'Invalid status code value received.')

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
