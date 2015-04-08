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

import fixtures
import mock


class BaseFixture(fixtures.Fixture):
    """Base class for test fixtures

    To create a test fixture, create a subclass of BaseFixture and define
    :meth:`setUp`


    Use :meth:`mock` to mock classes and map new methods to the mock'd class.
    """
    def mock(self, cls):
        """Convenience method for mock'ing classes.

        The class specified by :param:`cls` will be mock'd and returned to the
        caller.  Upon tearing down the fixture, the class will be reverted to
        its original representation.

        To mock a class, pass in the string path to the class, and save the
        returned value to a variable.  The mock'd version of the class that is
        returned will be used to redefine the class' behavior. ::

            mocked_class = mock('package.SomeClass')

        To replace a method in the mocked class, using a member method of the
        fixture allows the mock implementation to persist and share data
        between methods by using fixture member variables. ::

            mocked_class.method1 = self.method1

        See :meth:`cue.tests.fixtures.neutron.NeutronClient.setUp` for an
        example.

        :param cls: Class to be mock'd.  Pass in the string path to the class.
        :return: A mock'd version of the class.
        """
        class_name = ''
        if isinstance(cls, str):
            class_name = cls
        elif inspect.isclass(cls):
            class_name = "%s.%s" % (cls.__module__, cls.__name__)
        else:
            raise TypeError('Invalid parameter type provided')

        patch = mock.patch(class_name)
        mock_instance = patch.__enter__()
        self.addCleanup(patch.__exit__)
        mocked_cls = mock_instance.return_value
        return mocked_cls
