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
from oslo.config import cfg
from oslo.config import fixture as config_fixture

from cue.cmd import manage
from cue.manage import base as manage_base
from cue.manage import database as cue_db
from cue.tests.unit import base
from cue import version


class FakeClass():
    @manage_base.args('revision', nargs='?')
    def foo(self, revision):
        return


class TestManage(base.UnitTestCase):

    def setUp(self):

        super(TestManage, self).setUp()

        # setup config fixture
        self.CONF = config_fixture.Config()
        self.useFixture(self.CONF)

    def tearDown(self):

        super(TestManage, self).tearDown()
        cfg.CONF.reset()

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
        self.assertEqual("foo", manage.get_arg_string(args2))
        self.assertEqual("bar", manage.get_arg_string(args3))

    def test_fetch_func_args_database(self):
        """Asserts the cue.cmd.manage.fetch_func_args() returns the arguments

        First has to do some config to get the arg parsing to work properly.
        """

        category_opt = cfg.SubCommandOpt('category', title='Commands',
                                         help='Available Commands',
                                         handler=manage.add_command_parsers)
        cfg.CONF.register_cli_opt(category_opt)
        sys_argv = ["cue-manage", "database", "upgrade", "head"]
        cfg.CONF(sys_argv[1:], project='cue',
             version=version.version_info.version_string())

        cue_db_commands = cue_db.DatabaseCommands()
        args = manage.fetch_func_args(cue_db_commands.upgrade)
        self.assertEqual(args, ['head'])

    @mock.patch('oslo_db.sqlalchemy.migration_cli.manager.MigrationManager')
    def test_main_database(self, mock_migration_manager):
        """Tests cue.cmd.manage.main()

        Passes in args as though it were being called via the command line by
        overwriting sys.argv.  But don't worry, it gets set back in the tear
        down.
        """
        sys_argv = ["cue-manage", "database", "upgrade"]
        manage.main(sys_argv)

        self.assertEqual('cue', cfg.CONF.project)
        mock_migration_manager.assert_called_once()
