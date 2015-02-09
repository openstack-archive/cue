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

from cue.tests import base
from cue.tests.test_fixtures import nova
import os_tasklib.common as common_task
import os_tasklib.nova.get_vm_status as get_vm_status

from taskflow import engines
from taskflow.patterns import linear_flow


class GetVmStatusTests(base.TestCase):
    additional_fixtures = [
        nova.NovaClient
    ]

    task_store = {
        'nova_vm_id': "0",
    }

    def setUp(self):
        super(GetVmStatusTests, self).setUp()

        image_name = "cirros-0.3.2-x86_64-uec-kernel"
        flavor_name = "m1.tiny"

        # retrieve nova client API class
        self.nova_client = self.clients["nova"]

        self.image = self.nova_client.images.find(name=image_name)
        self.flavor = self.nova_client.flavors.find(name=flavor_name)

    def test_get_vm_status_task(self):
        """Verifies GetVMStatus task directly."""

        # create flow with "GetVmStatus" task
        self.flow = linear_flow.Flow('get vm status').add(
            get_vm_status.GetVmStatus(os_client=self.nova_client,
                                      provides='vm_status'))

        # create a vm
        new_instance = self.nova_client.servers.create(name="vm1",
                                                       image=self.image,
                                                       flavor=self.flavor)

        # set vm_id variable in TaskFlow's data store required for task
        GetVmStatusTests.task_store['nova_vm_id'] = new_instance.id

        # start engine to run task
        result = engines.run(self.flow, store=GetVmStatusTests.task_store)

        # verify vm_status key is present in result dictionary
        if 'vm_status' not in result:
            self.fail("Expected vm_status is was not returned by GetVmStatus "
                      "task.")

        # cleanup
        self.nova_client.servers.delete(new_instance)

    def test_get_vm_status_flow(self):
        """Verifies GetVmStatusTask in a successful retry flow

        This test simulates creating a new VM, then directly running a flow
        with the 'CheckFor' task which will fail until vm_status acquired from
        GetVmStatus task returns 'ACTIVE'.  The new VM will return 'BUILDING'
        for the first three times the VM is acquired, then will return
        'ACTIVE'
        """
        # configure custom vm_status list
        nova.VmStatusDetails.set_vm_status(['ACTIVE',
                                            'BUILDING',
                                            'BUILDING',
                                            'BUILDING'])

        # create flow with "GetVmStatus" task
        self.flow = linear_flow.Flow('wait for vm to become active',
                                     retry=retry.Times(10)).add(
            get_vm_status.GetVmStatus(os_client=self.nova_client,
                                      provides='vm_status'),
            common_task.CheckFor(rebind={'check_var': 'vm_status'},
                                 check_value='ACTIVE',
                                 retry_delay_seconds=1),
        )

        # create a vm
        new_instance = self.nova_client.servers.create(name="vm1",
                                                       image=self.image,
                                                       flavor=self.flavor)

        # set vm_id variable in TaskFlow's data store required for task
        GetVmStatusTests.task_store['nova_vm_id'] = new_instance.id

        # start engine to run task
        result = engines.run(self.flow, store=GetVmStatusTests.task_store)

        # verify vm_status key is in BUILD state
        self.assertEqual('ACTIVE', result['vm_status'],
                         "Invalid status received")

        # cleanup
        self.nova_client.servers.delete(new_instance)

    def test_get_vm_status_flow_timeout(self):
        """Verifies GetVmStatusTask in an unsuccessful retry flow

        This test simulates creating a new VM which does not build
        successively and results in an 'ERROR' state.  The flow will reach
        the maximum retry times and raise an 'AssertionError' for the expected
        failure.
        """
        # configure custom vm_status list
        nova.VmStatusDetails.set_vm_status(['BUILDING',
                                            'BUILDING',
                                            'BUILDING',
                                            'BUILDING',
                                            'BUILDING',
                                            'ERROR',
                                            'ERROR'])

        # create flow with "GetVmStatus" task
        self.flow = linear_flow.Flow('wait for vm to become active',
                                     retry=retry.Times(5)).add(
            get_vm_status.GetVmStatus(os_client=self.nova_client,
                                      provides='vm_status'),
            common_task.CheckFor(rebind={'check_var': 'vm_status'},
                                 check_value='ACTIVE',
                                 retry_delay_seconds=1),
        )

        # create a vm
        new_instance = self.nova_client.servers.create(name="vm1",
                                                       image=self.image,
                                                       flavor=self.flavor)

        # set vm_id variable in TaskFlow's data store required for task
        GetVmStatusTests.task_store['nova_vm_id'] = new_instance.id

        # start engine to run task and verify AssertRaises exception
        self.assertRaises(AssertionError, engines.run, self.flow,
                          store=GetVmStatusTests.task_store)

        # cleanup
        self.nova_client.servers.delete(new_instance)