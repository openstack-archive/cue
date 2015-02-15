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

import oslo_utils.reflection as reflection
import taskflow.task as task


class Lambda(task.Task):
    """General purpose Task to apply transformations to data

    This Task takes a function (lambda or otherwise) and
    applies it to input parameters.

    >>> from pprint import pprint
    >>> import taskflow.engines as engines
    >>> from taskflow.patterns import linear_flow
    >>> from os_tasklib.common import Lambda

    >>> l = lambda x, y: x + y
    >>> flow = linear_flow.Flow("test lambda flow")
    >>> flow = flow.add(Lambda(l, provides='z'))

    >>> input_store = { 'x': 2, 'y': 3 }
    >>> result = engines.run(flow, store=input_store)

    >>> pprint(result)
    {'x': 2, 'y': 3, 'z': 5}
    """
    def __init__(self, functor, name=None, requires=None, **kwargs):
        self.f_args = reflection.get_callable_args(functor)

        if requires and tuple(requires) != tuple(self.f_args):
            raise ValueError("requires must be the same as the functor "
                             "argument list")

        super(Lambda, self).__init__(name=name, requires=self.f_args, **kwargs)

        self.functor = functor

    def execute(self, **kwargs):
        common_keys = set(self.f_args).intersection(kwargs.keys())
        functor_kwargs = {k: kwargs[k] for k in common_keys}

        result = self.functor(**functor_kwargs)
        return result
