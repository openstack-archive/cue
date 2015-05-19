# -*- coding: utf-8 -*-
# Copyright 2014-2015 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

# Note: importing cue.cmd.manage will cause a timeout due to
#    the eventlet.monkey_patch call
from cue.cmd import manage
from cue.tests.unit import base


class FakeClass():
    def foo(self):
        return


class TestManage(base.UnitTestCase):

    def test_methods_of(self):
        """Test cue.cmd.manage methods_of."""

        my_fake_object = FakeClass()
        methods = manage.methods_of(my_fake_object)

        self.assertEqual(1, len(methods), "Number of methods found should "
                                          "have been 1, instead found: " +
                                          str(len(methods)))
        method_name = methods[0][0]
        self.assertEqual("foo", method_name, "Method found should have been "
                                             "\'foo\'.  Instead, found: "
                                             + str(method_name))

    @mock.patch('stevedore.extension.ExtensionManager')
    def test_get_available_commands_mock(self, mock_extension_manager):
        """Test cue.cmd.manage get_available_commands

        Asserts that the stevedore extension layer is called.
        """

        manage.get_available_commands()
        mock_extension_manager.assert_called_once_with('cue.manage')

    def test_get_available_commands(self):
        """Test cue.cmd.manage get_available_commands

        Asserts that the expected commands are available.
        """

        commands = manage.get_available_commands()

        self.assertEqual(3, len(commands.keys()),
                         "Expected to only find the three commands: database,"
                         " broker, taskflow.  Found "
                         + str(len(commands.keys())))

        expected_commands = ['database', 'broker', 'taskflow']
        for command in commands.keys():
            self.assertIn(command, expected_commands,
                          "Unexpected command returned from "
                          "get_available_commands: " + str(command) + ". The"
                          " only expected commands are: " +
                          str(expected_commands))

    def test_add_command_parsers(self):
        # How to get the subparser to pass in?
        pass

    def test_get_arg_string(self):
        """Test cue.cmd.manage get_arg_string."""

        args1 = "foobar"
        args2 = "-foo"
        args3 = "--bar"

        self.assertEqual("foobar", manage.get_arg_string(args1))

        # Todo (Dan) Fix the get_arg_string conditional so cases like arg2
        # Todo (Dan)  will properly return 'foo', not 'o'.
        self.assertEqual("o", manage.get_arg_string(args2))

        self.assertEqual("bar", manage.get_arg_string(args3))

    @mock.patch('oslo.db.sqlalchemy.migration_cli.manager.'
                'MigrationManager.version')
    def test_fetch_func_args(self, mock_version):
        # How to get the func to pass in?
        pass

    def test_main(self):
        # How to call properly?  This is meant to be called from cmd line.
        pass