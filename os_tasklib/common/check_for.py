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


__author__ = 'sputnik13'

from taskflow import task
from time import sleep


# TODO: This should be an "assert" task that takes a lambda function as
#       a predicate and maps inputs to the lambda function


class CheckFor(task.Task):
    def __init__(self, check_value, timeout_seconds=None, timeout_ms=None, name=None, **kwargs):
        self.check_value = check_value
        self.sleep_time = 0
        if timeout_seconds:
            self.sleep_time = timeout_seconds

        if timeout_ms:
            self.sleep_time += timeout_ms / 1000.0

        super(CheckFor, self).__init__(name=name, **kwargs)

    def execute(self, check_var, **kwargs):
        if check_var == self.check_value:
            return self.check_value
        else:
            #print "Check failed, expected %s, got %s" % (self.check_value, check_var)
            #if self.sleep_time != 0:
                #sleep(self.sleep_time)
            raise AssertionError("expected %s, got %s" % (self.check_value, check_var))

    def revert(self, check_var, *args, **kwargs):
        print "Check failed, expected %s, got %s" % (self.check_value, check_var)
        if self.sleep_time != 0:
            sleep(self.sleep_time)
