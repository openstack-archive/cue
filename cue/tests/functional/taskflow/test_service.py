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

import threading
import time

from oslo_utils import uuidutils
import taskflow.patterns.linear_flow as linear_flow
import taskflow.task
import zake.fake_client as zake_client

import cue.taskflow.client as tf_client
import cue.taskflow.service as tf_service
from cue.tests.functional import base


class TimesTwo(taskflow.task.Task):
    def execute(self, test_arg):
        return (test_arg * 2)


def create_flow():
    return linear_flow.Flow('test flow').add(
        TimesTwo(),
    )


class TaskflowServiceTest(base.FunctionalTestCase):
    def setUp(self):
        super(TaskflowServiceTest, self).setUp()
        _zk_client = zake_client.FakeClient()
        self.persistence = tf_client.create_persistence(client=_zk_client)
        self.jobboard = tf_client.create_jobboard("service_test",
                                                  persistence=self.persistence,
                                                  client=_zk_client)

        self.tf_client = tf_client.Client("service_test",
                                          persistence=self.persistence,
                                          jobboard=self.jobboard)

        self.tf_service = tf_service.ConductorService.create(
            host="service_test",
            jobboard=self.tf_client.jobboard,
            persistence=self.tf_client.persistence,
        )

    def tearDown(self):
        self.persistence.close()
        self.jobboard.close()

        super(TaskflowServiceTest, self).tearDown()

    def test_consume_background(self):
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
        self.assertGreater(pre_count, 0, "Job count is expected to be greater "
                           "than 0 !(%d > 0)" % pre_count)

        t = threading.Thread(target=self.tf_service.start)
        t.start()
        time.sleep(1)
        post_count = self.tf_client.jobboard.job_count
        expected = 0

        self.assertGreater(pre_count, post_count, "Job count before starting "
                           "the taskflow service is expected to be greater "
                           "than after starting the service !(%d > %d)"
                           % (pre_count, post_count))

        self.assertEqual(expected, post_count,
                         "expected %d jobs in the jobboard after a claim, "
                         "got %d" % (expected, post_count))

        self.tf_service.stop()
        self.tf_service.wait()
