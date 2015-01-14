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


class Assert(task.Task):
    def __init__(self, predicate, arglist=None, timeout_seconds=None, timeout_ms=None, name=None, **kwargs):
        self.predicate = predicate

        self.sleep_time = 0
        if timeout_seconds:
            self.sleep_time = timeout_seconds

        if timeout_ms:
            self.sleep_time += timeout_ms / 1000.0

        super(Assert, self).__init__(name=name, **kwargs)

    def execute(self, *args, **kwargs):
        print "execute"
        assert(self.predicate(*args, **kwargs))
        return (args, kwargs)

    def revert(self, *args, **kwargs):
        print "revert"
        print args, kwargs
        if self.sleep_time != 0:
            sleep(self.sleep_time)
