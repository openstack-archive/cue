# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from cue.tests import base
from cue.tests.fixtures import telnet
import os_tasklib.common.verify_network_task as verify_network_task

from taskflow import engines
from taskflow.patterns import linear_flow
import taskflow.retry as retry


class GetRabbitVmStatusTest(base.TestCase):
    additional_fixtures = [
        telnet.TelnetClient
    ]

    task_store = {
        'vm_ip': "0.0.0.0",
        'port': '5672'
    }

    def setUp(self):
        super(GetRabbitVmStatusTest, self).setUp()

    def test_get_rabbit_status(self):
        """Verifies GetRabbitVmStatus task directly."""

        # create flow with "GetRabbitVmStatus" task
        self.flow = linear_flow.Flow(name="wait for RabbitMQ ready state",
                         retry=retry.Times(5)).add(
            verify_network_task.VerifyNetwork(
                name="get RabbitMQ status",
                retry_delay_seconds=1))

        # start engine to run task
        engines.run(self.flow, store=GetRabbitVmStatusTest.task_store)

    def test_get_vm_status_flow(self):
        """Verifies GetRabbitVmStatus in a successful retry flow.

        This test simulates creating a cluster, then directly running a flow
        which will fail until telnet_status acquired from get_rabbit_vm_status
        task returns 'connect'.  Attempting the telnet connection will return
        'wait' for the first three times, then will return 'connected' once a
        telnet connection is made.  The node status should be in Active state.
        """
        # configure custom vm_status list
        telnet.TelnetStatusDetails.set_telnet_status(['connected',
                                                      'wait',
                                                      'wait',
                                                      'wait'])

        # create flow with "GetRabbitVmStatus" task
        self.flow = linear_flow.Flow(name="wait for RabbitMQ ready state",
                         retry=retry.Times(5)).add(
            verify_network_task.VerifyNetwork(
                name="get RabbitMQ status",
                retry_delay_seconds=1))

        # start engine to run task
        engines.run(self.flow, store=GetRabbitVmStatusTest.task_store)

    def test_get_vm_status_flow_fail(self):
        """Verifies GetRabbitVmStatus in an unsuccessful retry flow.

        This test simulates creating a cluster, then directly running a flow
        which will fail until the retry count has been exhausted.  Attempting
        the telnet connection will return 'wait' until retry count reaches
        limit and flow fails.  The node status should remain in Building state.
        """
        # configure custom vm_status list
        telnet.TelnetStatusDetails.set_telnet_status(['wait',
                                                      'wait',
                                                      'wait',
                                                      'wait'])

        # create flow with "GetRabbitVmStatus" task
        self.flow = linear_flow.Flow(name="wait for RabbitMQ ready state",
                         retry=retry.Times(3)).add(
            verify_network_task.VerifyNetwork(
                name="get RabbitMQ status",
                retry_delay_seconds=1))

        # start engine to run task
        self.assertRaises(IOError, engines.run, self.flow,
                          store=GetRabbitVmStatusTest.task_store)