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


class Map(task.Task):
    """General purpose Task to map a function to a list

    This Task mimics the behavior of Python's built-in map function.  The Task
    takes a functor (lambda or otherwise) and a list.  The list is specified
    using the requires argument of the Task.  When executed, this task calls
    map with the functor and list as arguments.  The resulting list from the
    call to map is then returned after execution.

    Each value of the returned list can be bound to individual names using
    the provides argument, following taskflow standard behavior.  Order is
    preserved in the returned list.

    >>> from pprint import pprint
    >>> import taskflow.engines as engines
    >>> from taskflow.patterns import linear_flow
    >>> from os_tasklib.common import Map

    >>> l = lambda x: x + x
    >>> flow = linear_flow.Flow("test lambda flow")
    >>> flow = flow.add(Map(l, requires=('x','y'), provides=('x2', 'y2')))

    >>> input_store = { 'x': 2, 'y': 3 }
    >>> result = engines.run(flow, store=input_store)

    >>> pprint(result)
    {'x': 2, 'x2': 4, 'y': 3, 'y2': 6}
    """
    def __init__(self, functor, requires, name=None, **kwargs):
        super(Map, self).__init__(name=name, requires=requires, **kwargs)

        f_args = reflection.get_callable_args(functor)
        if len(f_args) != 1:
            raise ValueError("functor must take exactly 1 argument")

        self.functor = functor
        self._requires = requires

    def execute(self, *args, **kwargs):
        l = [kwargs[r] for r in self._requires]
        return map(self.functor, l)
