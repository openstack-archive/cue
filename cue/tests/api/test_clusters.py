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
import anyjson

from cue.tests.api import api_common
from cue.tests import utils as test_utils


class TestListClusters(api_common.ApiCommon):
    def setUp(self):
        super(TestListClusters, self).setUp()

    def test_empty(self):
        data = self.get_json('/clusters')
        self.assertEqual([], data)

    def test_one(self):
        cluster = test_utils.create_db_test_cluster_from_objects_api(
            name=self.cluster_name)
        data = self.get_json('/clusters')

        self.assertEqual(len(data), 1, "Invalid number of clusters returned")

        self.validate_cluster_values(cluster, data[0])

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

        self.assertEqual(len(data), 5, "Invalid number of clusters returned")

        self.validate_cluster_values(cluster_0, data[0])
        self.validate_cluster_values(cluster_1, data[1])
        self.validate_cluster_values(cluster_2, data[2])
        self.validate_cluster_values(cluster_3, data[3])
        self.validate_cluster_values(cluster_4, data[4])


class TestCreateCluster(api_common.ApiCommon):
    def setUp(self):
        super(TestCreateCluster, self).setUp()

    def test_create_empty(self):
        """test create an empty cluster."""
        #TODO(dagnello): should this functionality be allowed or return error
        #  inv params?

    def test_create_size_one(self):
        """test create a cluster with one node."""
        api_cluster = test_utils.create_api_test_cluster(
            name=self.cluster_name,
            size=1)
        cluster_dict = api_cluster.as_dict()
        cluster_json = anyjson.serialize(cluster_dict)
        header = {'Content-Type': 'application/json'}
        data = self.post_json('/clusters', params=cluster_json, headers=header,
                              expect_errors=True)
        print(data)

    def test_create_size_three(self):
        """test create a cluster with three nodes."""

    def test_create_size_five(self):
        """test create a cluster with five nodes."""

    def test_create_invalid_size(self):
        """test with invalid size parameter."""

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
