# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_utils import uuidutils
import taskflow.patterns.linear_flow as linear_flow
import taskflow.task


import cue.taskflow.client as tf_client
from cue.tests.functional import api
from cue.tests.functional import base
from cue.tests.functional import utils as test_utils


class TimesTwo(taskflow.task.Task):
    def execute(self, test_arg):
        return (test_arg * 2)


def create_flow():
    return linear_flow.Flow('test flow').add(
        TimesTwo(),
    )


class TaskflowClientTest(base.FunctionalTestCase):
    def setUp(self):
        super(TaskflowClientTest, self).setUp()
        self.tf_client = tf_client.get_client_instance()

    def tearDown(self):
        super(TaskflowClientTest, self).tearDown()

    def test_post_job(self):
        job_args = {
            'test_arg': 5
        }
        tx_uuid = uuidutils.generate_uuid()

        pre_count = self.tf_client.jobboard.job_count
        job = self.tf_client.post(create_flow, job_args, tx_uuid=tx_uuid)
        post_count = self.tf_client.jobboard.job_count
        expected = pre_count + 1

        self.assertEqual(expected, post_count,
                         "expected %d jobs in the jobboard after a post, "
                         "got %d" % (expected, post_count))

        job_list = self.tf_client.joblist()
        self.assertEqual(expected, len(job_list),
                         "expected %d jobs in the joblist, "
                         "got %d" % (expected, post_count))
        posted_job = {}
        for j in job_list:
            if j.uuid == job.uuid:
                posted_job = j

        self.assertDictEqual(posted_job.__dict__, job.__dict__,
                             "Job in jobboard differs from job returned by "
                             "Client.post method")

        pre_count = self.tf_client.jobboard.job_count
        self.tf_client.delete(job=job)
        post_count = self.tf_client.jobboard.job_count
        expected = pre_count - 1

        self.assertEqual(expected, post_count,
                         "expected %d jobs in the jobboard after a claim, "
                         "got %d" % (expected, post_count))


class ApiTaskFlowClientTest(api.APITest):

    def setUp(self):
        super(ApiTaskFlowClientTest, self).setUp()
        self.tf_client = tf_client.get_client_instance()

    def test_create_cluster_api(self):
        """This test verifies create cluster job is posted from REST API."""
        api_cluster = test_utils.create_api_test_cluster(size=1,
                                                network_id=(
                                                [uuidutils.generate_uuid()]))
        pre_count = self.tf_client.jobboard.job_count
        self.post_json('/clusters', params=api_cluster,
                       headers=self.auth_headers, status=202)
        post_count = self.tf_client.jobboard.job_count
        expected = pre_count + 1

        self.assertEqual(expected, post_count,
                         "expected %d jobs in the jobboard after a post, "
                         "got %d" % (expected, post_count))

    def test_delete_cluster_api(self):
        """This test verifies delete cluster job is posted from REST API."""
        cluster = test_utils.create_db_test_cluster_from_objects_api(
            self.context, name="test_cluster")
        pre_count = self.tf_client.jobboard.job_count
        self.delete('/clusters/' + cluster.id, headers=self.auth_headers)
        post_count = self.tf_client.jobboard.job_count
        expected = pre_count + 1

        self.assertEqual(expected, post_count,
                         "expected %d jobs in the jobboard after a post, "
                         "got %d" % (expected, post_count))
