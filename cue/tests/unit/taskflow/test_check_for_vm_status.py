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

import mock

from cue.common import exception as cue_exceptions
import cue.taskflow.task.check_for_vm_status as check_for_vm_status
from cue.tests.unit import base


class TaskflowCheckVmStatusTest(base.UnitTestCase):
    def setUp(self):
        super(TaskflowCheckVmStatusTest, self).setUp()

    def tearDown(self):
        super(TaskflowCheckVmStatusTest, self).tearDown()

    @mock.patch('time.sleep')
    def test_check_vm_status_ms(self, mock_sleep):
        check_task = check_for_vm_status.CheckForVmStatus(
            name="check vm status",
            details="waiting for ACTIVE VM status",
            retry_delay_ms=1000,
        )
        check_task.revert('BUILD')

        self.assertEqual(1.0, mock_sleep.call_args[0][0])

    def test_check_vm_status_no_details(self):
        check_task = check_for_vm_status.CheckForVmStatus(
            name="check vm status",
        )
        try:
            check_task.execute('BUILD')
        except cue_exceptions.VmBuildingException as err:
            self.assertEqual(cue_exceptions.VmBuildingException.message,
                             err.message)
        else:
            self.fail("Expected VmBuildingException")
