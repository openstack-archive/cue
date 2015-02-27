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

import cue.client as client
from cue.tests import base
from cue.tests.test_fixtures import nova
from cue.tests.test_fixtures import telnet
import cue.taskflow.task as cue_task

from taskflow import engines
from taskflow.patterns import linear_flow
import taskflow.retry as retry

import uuid


class CheckOrRestartRabbitTest(base.TestCase):
    additional_fixtures = [
        nova.NovaClient,
        telnet.TelnetClient
    ]

    task_store = {
        'vm_ip': "0.0.0.0",
        'vm_info': str(uuid.uuid4()),
        'port': '5672'
    }

    def setUp(self):
        super(CheckOrRestartRabbitTest, self).setUp()

        self.nova_client = client.nova_client()

        rabbitmq_retry_strategy = [
            'check',
            'check',
            'check',
            'check',
            'restart',
        ]

        retry_controller = retry.ForEach(rabbitmq_retry_strategy,
                                         "retry check RabbitMQ",
                                         provides="retry_strategy")
        self.flow = linear_flow.Flow(name="wait for RabbitMQ ready state",
                                     retry=retry_controller).add(
            cue_task.CheckOrRestartRabbitMq(
                os_client=self.nova_client,
                name="get RabbitMQ status %s",
                rebind={'action': "retry_strategy"},
                retry_delay_seconds=1))

    def test_get_rabbit_status(self):
        """Verifies GetRabbitVmStatus task directly."""

        # start engine to run task
        engines.run(self.flow, store=CheckOrRestartRabbitTest.task_store)

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
        # start engine to run task
        engines.run(self.flow, store=CheckOrRestartRabbitTest.task_store)
        self.assertFalse(self.nova_client.servers.reboot.called)

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
                                                      'wait',
                                                      'wait',
                                                      'wait'])

        # start engine to run task
        self.assertRaises(IOError, engines.run, self.flow,
                          store=CheckOrRestartRabbitTest.task_store)
        self.assertTrue(self.nova_client.servers.reboot.called)
