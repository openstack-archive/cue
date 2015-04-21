# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Authors: Daniel Allegood <daniel.allegood@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Copyright [2014] Hewlett-Packard Development Company, L.P.
# limitations under the License.

import contextlib
import re
import os
import six
import StringIO
import sys

from alembic import config as alembic_migration

from collections import OrderedDict
# from cue.db.sqlalchemy import api as cue_sqla_api
# from cue.db.sqlalchemy import base as sqlalchemy_base
# from cue.manage import database as cue_db
# from cue.tests.functional import base
# from oslo_config import cfg
# from oslo_config import fixture as config_fixture
# from oslo_db import options as db_options
# from oslo_db.sqlalchemy import test_migrations
from oslotest import base as oslo_base
import testtools
#
# from oslo.db.sqlalchemy import session as oslo_session

from alembic import config as alembic_config
from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext
from alembic import command as alembic_command
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

# CONF = cfg.CONF


@contextlib.contextmanager
def stdout_redirect(where):
    sys.stdout = where
    try:
        yield where
    finally:
        sys.stdout = sys.__stdout__


# class MigrationFunctionalTests(oslo_base.BaseTestCase):
# class MigrationFunctionalTests(base.FunctionalTestCase):
class MigrationFunctionalTests(testtools.TestCase):
    cue_manage_database = None
    sorted_revision_list = None
    head = None
    engine = None

    def setUp(self):
        super(MigrationFunctionalTests, self).setUp()
        print "enter setup"


        # cue_sqla_api._FACADE = None
        # reload(cue_sqla_api)
        # reload(sqlalchemy_base)
        # reload(cue_db)

        # alembic_migration.Config

        # self.old_connection = cfg.CONF.database.connection

        # self.flags(connection="sqlite:////tmp/test_migration.db",
        #            group="database")
        # self.flags(connection="sqlite://", group="database")

        # self.connection = "sqlite:////tmp/test_migration.db"

        # self.CONF = config_fixture.Config()
        # self.cfg = self.useFixture(self.CONF)

        # cfg.CONF.set_override('connection', self.connection, group='database')
        # cfg.CONF.set_override('state_path', '/tmp')
        # cfg.CONF.set_override('sqlite_db', 'test_migration.db')


        # self.CONF.config(connection=self.connection, group='database')
        # self.CONF.config(state_path="/tmp")
        # self.CONF.config(sqlite_db="test_migration.db")
        # db_options.set_defaults(cfg.CONF, connection="sqlite:////tmp/test_migration.db")

        # self.cue_manage_database = cue_db.DatabaseCommands()

        # This Ordered Dictionary should be maintained to track each new
        # revision version that comes in.  The 'HEAD' revision is expected to
        # be in index len(sorted_revision_list)-1.
        self.sorted_revision_list = OrderedDict([
            ('None', []),
            ('236f63c96b6a', ['clusters', 'endpoints', 'nodes']),
            ('3917e931a55a', ['clusters', 'endpoints', 'nodes', 'broker',
                              'broker_metadata'])
        ])

        self.alembic_cfg = alembic_config.Config(os.path.join(os.path.dirname(__file__),
                            '..', '..', '..', '..', 'db', 'sqlalchemy', 'alembic.ini'))
        BASE = declarative_base()
        engine = create_engine('sqlite:////tmp/migration_test.db')
        BASE.metadata.bind = engine
        BASE.metadata.create_all(engine)

        connection = engine.connect()
        self.alembic_cfg.connection = connection
        context = MigrationContext.configure(connection)
        script = ScriptDirectory.from_config(self.alembic_cfg)
        head_revision = script.get_current_head()
        context._ensure_version_table()
        context.stamp(script, head_revision)

        print "\n\nTEST"
        alembic_command.downgrade(self.alembic_cfg, "base")
        alembic_command.current
        print "\n---------------\n\n"

        num_revisions = len(self.sorted_revision_list)
        self.head = self.sorted_revision_list.keys()[num_revisions-1]



        # facade = oslo_session.EngineFacade.from_config(cfg.CONF, sqlite_fk=True)

        # self.engine = cue_sqla_api.get_engine()
        # sqlalchemy_base.BASE.metadata.bind = self.engine
        # #
        # session = cue_sqla_api.get_session()
        # session.bind = self.engine
        # print ""


    def tearDown(self):
        super(MigrationFunctionalTests, self).tearDown()

        # cfg.CONF.clear_override('connection', group='database')
        # cfg.CONF.clear_override('state_path')
        # cfg.CONF.clear_override('sqlite_db')

        # cfg.CONF.set_override('connection', self.old_connection, group='database')

        if os.path.exists("/tmp/test_migration.db"):
            os.remove("/tmp/test_migration.db")
        print ""

    def flags(self, group=None, **kw):
        """Override flag variables for a test."""
        for k, v in six.iteritems(kw):
            CONF.set_override(k, v, group)

    # def test_get_revision_id(self):
    #     """Runs 'cue-manage database version' and confirms revision id is
    #     printed to stdout"""
    #
    #     with stdout_redirect(StringIO.StringIO()) as new_stdout:
    #         self.cue_manage_database.version()
    #
    #     new_stdout.seek(0)
    #     std_out = new_stdout.read().strip()
    #
    #     reg = "\w* ([0-9a-z]{8}|None)"
    #     match = re.match(reg, std_out)
    #     match = match.group(0) if match is not None else None
    #
    #     self.assertIsNotNone(match, "Version info was not printed.  " +
    #                          "Instead found:  \"" + std_out + "\"")

    def test_upgrade(self):
        """This test will run incremental upgrades and compare the existing
        tables against the 'expected' through the sorted_revision_list."""

        print "enter upgrade"

        # # cfg.CONF.set_override('connection', self.connection, group='database')
        #
        # # tables = sqlalchemy_base.BASE.metadata.sorted_tables
        #
        # # Confirm initialization since this test isn't guaranteed to be the
        # # first one ran after setUp().
        # if cue_db.get_manager().version() is not None:
        #     print "upgrade init downgrade"
        #     self.cue_manage_database.downgrade('base')
        #
        # for expected_version in self.sorted_revision_list:
        #     if expected_version is 'None':
        #         # Skipping if we are at the initial version since we
        #         # cannot upgrade to the initial.
        #         continue
        #
        #     print "\nupgrade increment upgrade"
        #     self.cue_manage_database.upgrade("+1")
        #
        #     print "\nupgrade increment check version"
        #     current_version = str(cue_db.get_manager().version())
        #     current_tables = []
        #     for t in tables:
        #         if t.exists():
        #             current_tables.append(t.name)
        #
        #     self.assertEqual(expected_version,
        #                      current_version,
        #                      "The current database revision id (" +
        #                      current_version + ") was not expected.  Check" +
        #                      " the test setup.")
        #
        #     expected_tables = self.sorted_revision_list[current_version]
        #
        #     for table in expected_tables:
        #         self.assertIn(table, current_tables, "Failed to find the " +
        #                       "expected table \'" + str(table) + "\' in the " +
        #                       "list of current tables.")
        # print "exiting upgrade"

    # def test_downgrade(self):
    #     """This test will run incremental downgrades and compare the existing
    #     tables against the 'expected' through the sorted_revision_list."""
    #
    #     tables = sqlalchemy_base.BASE.metadata.sorted_tables
    #
    #     # Confirm initialization since this test isn't guaranteed to be the
    #     # first one ran after setUp().
    #     print "Getting version 1"
    #     if cue_db.get_manager().version() is not self.head:
    #         print "upgrading to head"
    #         self.cue_manage_database.upgrade("head")
    #
    #     for expected_version in reversed(self.sorted_revision_list):
    #         if expected_version == self.head:
    #             # Skipping if we are at 'head' since we cannot downgrade
    #             # to the head.
    #             continue
    #
    #         print "Downgrading"
    #         self.cue_manage_database.downgrade("-1")
    #
    #         print "Print version"
    #         current_version = str(cue_db.get_manager().version())
    #         current_tables = []
    #         for t in tables:
    #             if t.exists():
    #                 current_tables.append(t.name)
    #
    #         self.assertEqual(expected_version,
    #                          current_version,
    #                          "The current database revision id (" +
    #                          current_version + ") was not expected.  Check " +
    #                          " the test setup.")
    #
    #         expected_tables = self.sorted_revision_list[current_version]
    #
    #         for table in expected_tables:
    #             self.assertIn(table, current_tables)
    #     print "Exiting downgrade"