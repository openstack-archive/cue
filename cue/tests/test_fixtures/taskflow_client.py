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

    def setUp(self):
        """Set up test fixture and apply all method overrides."""
        super(TaskFlowClient, self).setUp()

        taskflow_client = self.mock('cue.taskflow.client.Client')
        taskflow_client.persistence = self.persistence
        taskflow_client.jobboard = self.jobboard
        taskflow_client.post = self.post

    def persistence(self, conf=None, **kwargs):
        """Mock'd version of neutronclient...create_port().

        Create a Neutron network port.

        :param body: Dictionary with port information.
        :return: An updated copy of the 'body' that was passed in, with other
                 information populated.
        """

        backend = 'mocked_backend'

        return backend

    def jobboard(self, board_name, conf=None, persistence=None, **kwargs):
        """Mock'd version of neutronclient...create_network().

        Create a Neutron network.

        :param body: Dictionary with network information.
        :return: An updated copy of the 'body' that was passed in, with other
                 information populated.
        """
        if board_name is None:
            board_name = 'sample_board_name'

        jobboard = 'mocked_jobboard'

        return jobboard

    def post(self, flow_factory, job_args=None, flow_args=None,
             flow_kwargs=None, tx_uuid=None):
        """Mock'd version of neutronclient...list_ports().

        List available ports.

        :param retrieve_all: Set to true to retrieve all available ports
        """
        return