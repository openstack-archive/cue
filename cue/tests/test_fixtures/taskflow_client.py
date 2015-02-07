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

import cue.tests.test_fixtures.base as base


class TaskFlowClient(base.BaseFixture):
    """A test fixture to simulate a TaskFlow client

    This class is used in test cases to simulate a TaskFlow client connection
    in the absence of a working TaskFlow setup with zookeeper.
    """

    def __del__(self):
        return

    def setUp(self):
        """Set up test fixture and apply all method overrides."""
        super(TaskFlowClient, self).setUp()

        taskflow_client = self.mock('cue.taskflow.client.Client')
        taskflow_client.create_persistence = self.persistence
        taskflow_client.create_jobboard = self.jobboard
        taskflow_client.post = self.post

    def persistence(self, conf=None, **kwargs):
        """Mock'd version of TaskFlow Client ...persistence().

        Creating a persistence backend.

        :param conf: Configuration parameters for the persistence backend.
        :param kwargs: Keyword arguments to be passed forward to the
                       persistence backend constructor
        :return: A persistence backend instance (mocked).
        """

        backend = 'mocked_backend'

        return backend

    def jobboard(self, board_name, conf=None, persistence=None, **kwargs):
        """Mock'd version of TaskFlow Client ...jobboard().

        Factory method for creating a jobboard backend instance

        :param board_name: Name of the jobboard
        :param conf: Configuration parameters for the jobboard backend.
        :param persistence: A persistence backend instance to be used with the
                            jobboard.
        :param kwargs: Keyword arguments to be passed forward to the
                       persistence backend constructor
        :return: A persistence backend instance (mocked).
        """
        if board_name is None:
            board_name = 'sample_board_name'

        jobboard = 'mocked_jobboard'

        return jobboard

    def post(self, flow_factory, job_args=None, flow_args=None,
             flow_kwargs=None, tx_uuid=None):
        """Mock'd version of TaskFlow Client ...post().

        Method for posting a new job to the jobboard

        :param flow_factory: Flow factory function for creating a flow instance
                             that will be executed as part of the job.
        :param job_args: 'store' arguments to be supplied to the engine
                         executing the flow for the job
        :param flow_args: Positional arguments to be passed to the flow factory
                          function
        :param flow_kwargs: Keyword arguments to be passed to the flow factory
                            function
        :param tx_uuid: Transaction UUID which will be injected as 'tx_uuid' in
                        job_args.  A tx_uuid will be generated if one is not
                        provided as an argument.
        :return: A taskflow.job.Job instance that represents the job that was
                 posted.
        """
        return