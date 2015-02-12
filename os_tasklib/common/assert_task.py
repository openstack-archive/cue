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


import inspect
import time

import taskflow.task as task


class Assert(task.Task):
    """General purpose Task to assert a condition

    This Task takes a function (lambda or otherwise) as a condition and
    applies it to input parameters.  The result is then asserted to be
    True.

    Input parameters must be specifically required by the task using the
    requires argument in the task constructor.

    >>> from pprint import pprint
    >>> import taskflow.engines as engines
    >>> from taskflow.patterns import linear_flow
    >>> from os_tasklib.common import Assert

    >>> l = lambda x, y: x == y
    >>> flow = linear_flow.Flow("test assert flow")
    >>> flow = flow.add(Assert(l, requires=('x','y')))

    >>> good_input = { 'x': 3, 'y': 3 }
    >>> result = engines.run(flow, store=good_input)
    >>> pprint(result)
    {'x': 3, 'y': 3}

    As shown below, a failed assertion will thrown an AssertionError.  In
    taskfow, this will also result in tasks that precede the failed Assert Task
    to be reverted.

    >>> bad_input = { 'x': 2, 'y': 3 }
    >>> result = engines.run(flow, store=bad_input)
    Traceback (most recent call last):
    ...
    AssertionError

    """
    def __init__(self,
                 condition,
                 timeout_seconds=None,
                 timeout_ms=None,
                 name=None,
                 **kwargs):
        super(Assert, self).__init__(name=name, **kwargs)

        self.condition = condition
        self.argspec = inspect.getargspec(condition)

        self.sleep_time = 0
        if timeout_seconds:
            self.sleep_time = timeout_seconds

        if timeout_ms:
            self.sleep_time += timeout_ms / 1000.0

    def execute(self, *args, **kwargs):
        common_keys = set(self.argspec.args).intersection(kwargs.keys())
        condition_kwargs = {k: kwargs[k] for k in common_keys}

        assert(self.condition(**condition_kwargs))

    def revert(self, *args, **kwargs):
        if self.sleep_time != 0:
            time.sleep(self.sleep_time)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
