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

import time

import taskflow.task as task


class CheckFor(task.Task):
    def __init__(self,
                 check_value,
                 retry_delay_seconds=None,
                 retry_delay_ms=None,
                 name=None,
                 **kwargs):
        super(CheckFor, self).__init__(name=name, **kwargs)

        self.check_value = check_value
        self.sleep_time = 0
        if retry_delay_seconds:
            self.sleep_time = retry_delay_seconds

        if retry_delay_ms:
            self.sleep_time += retry_delay_ms / 1000.0

    def execute(self, check_var, **kwargs):
        if check_var == self.check_value:
            return self.check_value
        else:
            raise AssertionError("expected %s, got %s" %
                                 (self.check_value, check_var))

    def revert(self, check_var, *args, **kwargs):
        if self.sleep_time != 0:
            time.sleep(self.sleep_time)