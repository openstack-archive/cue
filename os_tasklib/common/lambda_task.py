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

import taskflow.task as task


class Lambda(task.Task):
    """General purpose Task to apply transformations to data

    This Task takes a function (lambda or otherwise) and
    applies it to input parameters.

    Input parameters must be specifically required by the task using the
    requires argument in the task constructor.

    >>> from pprint import pprint
    >>> import taskflow.engines as engines
    >>> from taskflow.patterns import linear_flow

    >>> l = lambda x, y: x + y
    >>> flow = linear_flow.Flow("test lambda flow")
    >>> flow = flow.add(Lambda(l, provides='z', requires=('x','y')))

    >>> input_store = { 'x': 2, 'y': 3 }
    >>> result = engines.run(flow, store=input_store)

    >>> pprint(result)
    {'x': 2, 'y': 3, 'z': 5}
    """
    def __init__(self, functor, name=None, **kwargs):
        super(Lambda, self).__init__(name=name, **kwargs)

        self.functor = functor
        self.argspec = inspect.getargspec(functor)

    def execute(self, *args, **kwargs):
        common_keys = set(self.argspec.args).intersection(kwargs.keys())
        functor_kwargs = {k: kwargs[k] for k in common_keys}

        result = self.functor(**functor_kwargs)
        return result
