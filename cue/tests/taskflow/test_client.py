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
import contextlib

from oslo.utils import uuidutils
import taskflow.patterns.linear_flow as linear_flow
import taskflow.task
import zake.fake_client as fake_client

import cue.taskflow.client as tf_client
import cue.tests.base as base


class TimesTwo(taskflow.task.Task):
    def execute(self, test_arg):
        return (test_arg * 2)


def create_flow():
    return linear_flow.Flow('test flow').add(
        TimesTwo(),
    )


class TaskflowClientTest(base.TestCase):
    def setUp(self):
        super(TaskflowClientTest, self).setUp()
        self._zk_client = fake_client.FakeClient()
        self.persistence = tf_client.Client.persistence(client=self._zk_client)
        with contextlib.closing(self.persistence.get_connection()) as conn:
            conn.upgrade()
        self.jobboard = tf_client.Client.jobboard("test_board",
                                                  persistence=self.persistence,
                                                  client=self._zk_client)
        self.tf_client = tf_client.Client("test_client",
                                          persistence=self.persistence,
                                          jobboard=self.jobboard)

    def tearDown(self):
        super(TaskflowClientTest, self).tearDown()

    def test_post_job(self):
        job_args = {
            'test_arg': 5
        }
        tx_uuid = uuidutils.generate_uuid()

        pre_count = self.jobboard.job_count
        job = self.tf_client.post(create_flow, job_args, tx_uuid=tx_uuid)
        post_count = self.jobboard.job_count
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

        pre_count = self.jobboard.job_count
        self.tf_client.delete(job=job)
        post_count = self.jobboard.job_count
        expected = pre_count - 1

        self.assertEqual(expected, post_count,
                         "expected %d jobs in the jobboard after a claim, "
                         "got %d" % (expected, post_count))
