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
from six import moves
import taskflow.task as task


class Reduce(task.Task):
    """General purpose Task to reduce a list by applying a function

    This Task mimics the behavior of Python's built-in reduce function.  The
    Task takes a functor (lambda or otherwise) and a list.  The list is
    specified using the requires argument of the Task.  When executed, this
    task calls reduce with the functor and list as arguments.  The resulting
    value from the call to reduce is then returned after execution.

    >>> from pprint import pprint
    >>> import taskflow.engines as engines
    >>> from taskflow.patterns import linear_flow
    >>> from os_tasklib.common import Reduce

    >>> l = lambda x, y: x + y
    >>> flow = linear_flow.Flow("test lambda flow")
    >>> flow = flow.add(Reduce(l, provides='sum', requires=('x','y','z')))

    >>> input_store = { 'x': 2, 'y': 3 , 'z': 4}
    >>> result = engines.run(flow, store=input_store)

    >>> pprint(result)
    {'sum': 9, 'x': 2, 'y': 3, 'z': 4}
    """
    def __init__(self, functor, requires, name=None, **kwargs):
        super(Reduce, self).__init__(name=name, requires=requires, **kwargs)

        if len(requires) < 2:
            raise ValueError("Minimum of 2 arguments required")

        f_args = reflection.get_callable_args(functor)
        if len(f_args) != 2:
            raise ValueError("functor must take exactly 2 arguments")

        self.functor = functor

    def execute(self, *args, **kwargs):
        l = [kwargs[r] for r in self.requires]
        return moves.reduce(self.functor, l)
