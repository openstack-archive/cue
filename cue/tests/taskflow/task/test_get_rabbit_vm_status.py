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

import taskflow.retry as retry

import cue.taskflow.task.get_rabbit_vm_status as get_rabbit_vm_status
from cue.tests import base
from cue.tests.test_fixtures import telnet
import os_tasklib.common as common_task

from taskflow import engines
from taskflow.patterns import linear_flow

SHARED_CONF = {
    'connection': 'zookeeper',
}


class GetRabbitVmStatusTest(base.TestCase):
    additional_fixtures = [
        telnet.TelnetClient
    ]

    task_store = {
        'vm_ip': "0.0.0.0",
        'rabbit_port': '5672'
    }

    def setUp(self):
        super(GetRabbitVmStatusTest, self).setUp()

    def test_get_rabbit_status(self):
        """Verifies GetVMStatus task directly."""

        # create flow with "GetRabbitVmStatus" task
        self.flow = linear_flow.Flow('get vm status').add(
            get_rabbit_vm_status.GetRabbitVmStatus(provides='rabbit_status'))

        # start engine to run task
        result = engines.run(self.flow, store=GetRabbitVmStatusTest.task_store)

        self.assertEqual('ready', result['rabbit_status'], 'Unexpected '
                                                           'RabbitMQ status'
                                                           'received')

    def test_get_vm_status_flow(self):
        """Verifies GetVmStatusTask in a successful retry flow

        This test simulates creating a new VM, then directly running a flow
        with the 'CheckFor' task which will fail until vm_status acquired from
        GetVmStatus task returns 'ACTIVE'.  The new VM will return 'BUILDING'
        for the first three times the VM is acquired, then will return
        'ACTIVE'
        """
        # configure custom vm_status list
        telnet.TelnetStatusDetails.set_vm_status(['ready',
                                                  None,
                                                  None,
                                                  None])

        # create flow with "GetRabbitVmStatus" task
        self.flow = linear_flow.Flow('wait for vm to become active',
                                     retry=retry.Times(10)).add(
            get_rabbit_vm_status.GetRabbitVmStatus(provides='rabbit_status'),
            common_task.CheckFor(rebind={'check_var': 'rabbit_status'},
                                 check_value='ready',
                                 timeout_seconds=1),
        )

        # start engine to run task
        result = engines.run(self.flow, store=GetRabbitVmStatusTest.task_store)

        # verify vm_status key is in BUILD state
        self.assertEqual('ready', result['rabbit_status'],
                         "Invalid status received")