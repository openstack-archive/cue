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

import taskflow.retry as tf_retry

from cue.common import exception as cue_exceptions
import cue.taskflow.retry.exception_times as retry
from cue.tests.unit import base


class TaskflowExceptionTimesTest(base.UnitTestCase):
    def setUp(self):
        super(TaskflowExceptionTimesTest, self).setUp()

    def tearDown(self):
        super(TaskflowExceptionTimesTest, self).tearDown()

    def test_revert_action(self):

        retry_exception_times = retry.ExceptionTimes(
            revert_exception_list=[cue_exceptions.VmErrorException],
            attempts=10,
            revert_all=False)
        self.assertEqual(tf_retry.REVERT, retry_exception_times._revert_action)

    def test_revert_action_empty_exception_list(self):

        retry_exception_times = retry.ExceptionTimes(
            revert_exception_list=None,
            attempts=10,
            revert_all=False)
        self.assertEqual([], retry_exception_times._revert_exception_list)