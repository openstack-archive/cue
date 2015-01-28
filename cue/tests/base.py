# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
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

"""Base classes for our unit tests.

Allows overriding of flags for use of fakes, and some black magic for
inline callbacks.

"""

from cue.common import context as cue_context
from cue.db.sqlalchemy import api as db_api
from cue.db.sqlalchemy import base as db_base
from cue.manage import database
from cue.tests import fixture

import os
import shutil

import fixtures
import mock
from oslo.config import cfg
from oslo.config import fixture as cfg_fixture
from oslo.utils import timeutils
from oslotest import base
import six


test_opts = [
    cfg.StrOpt('sqlite_clean_db',
               default='clean.sqlite',
               help='File name of clean sqlite database.'),
    cfg.BoolOpt('fake_tests',
                default=True,
                help='Whether to use everything for testing.'), ]

CONF = cfg.CONF
CONF.register_opts(test_opts)

_DB_CACHE = None


class Database(fixtures.Fixture):

    def __init__(self, db_session, db_migrate, sql_connection, sqlite_db,
                 sqlite_clean_db):
        self.sql_connection = sql_connection
        self.sqlite_db = sqlite_db
        self.sqlite_clean_db = sqlite_clean_db
        self.engine = db_session.get_engine()
        self.engine.dispose()
        conn = self.engine.connect()

        if sql_connection == "sqlite://":
            self.setup_sqlite(db_migrate)
        else:
            testdb = os.path.join(CONF.state_path, sqlite_db)
            db_migrate.upgrade('head')
            if os.path.exists(testdb):
                return
        if sql_connection == "sqlite://":
            conn = self.engine.connect()
            self._DB = "".join(line for line in conn.connection.iterdump())
            self.engine.dispose()
        else:
            cleandb = os.path.join(CONF.state_path, sqlite_clean_db)
            shutil.copyfile(testdb, cleandb)

    def setUp(self):
        super(Database, self).setUp()
        if self.sql_connection == "sqlite://":
            conn = self.engine.connect()
            conn.connection.executescript(self._DB)
            self.addCleanup(self.engine.dispose)  # pylint: disable=E1101
        else:
            shutil.copyfile(
                os.path.join(CONF.state_path, self.sqlite_clean_db),
                os.path.join(CONF.state_path, self.sqlite_db),
            )

    def setup_sqlite(self, db_migrate):
        if db_migrate.version():
            return
        db_base.BASE.metadata.create_all(self.engine)
        db_migrate.stamp('head')


class StubOutForTesting(object):
    def __init__(self, parent):
        self.parent = parent

    def Set(self, obj, attr_name, new_attr):
        stub = mock.patch.object(obj, attr_name, new_attr)
        stub.start()
        self.parent.addCleanup(stub.stop)


class TestCase(base.BaseTestCase):
    """Test case base class for all unit tests."""

    additional_fixtures = []

    def setUp(self):
        """Run before each test method to initialize test environment."""
        super(TestCase, self).setUp()
        self.context = cue_context.RequestContext(auth_token="auth_xxx",
                                                  user='user',
                                                  tenant='tenant',
                                                  )

        self.CONF = self.useFixture(cfg_fixture.Config(cfg.CONF)).conf
        self.flags(state_path='/tmp')
        # NOTE(vish): We need a better method for creating fixtures for tests
        #             now that we have some required db setup for the system
        #             to work properly.
        self.start = timeutils.utcnow()

        self.log_fixture = self.useFixture(fixtures.FakeLogger())
        self.useFixture(fixtures.NestedTempfile())
        self.useFixture(fixtures.TempHomeDir())

        self.flags(connection="sqlite://", group="database")

        global _DB_CACHE
        if not _DB_CACHE:
            _DB_CACHE = Database(
                db_api,
                database.get_manager(),
                sql_connection=CONF.database.connection,
                sqlite_db=CONF.sqlite_db,
                sqlite_clean_db=CONF.sqlite_clean_db,
            )
        self.useFixture(_DB_CACHE)

        self.stubs = StubOutForTesting(self)
        self.injected = []
        # This will be cleaned up by the NestedTempfile fixture
        # CONF.set_override('lock_path', tempfile.mkdtemp())
        self.policy = self.useFixture(fixture.PolicyFixture())

        # self.CONF.register_opt('config_dir')

        self.session = db_api.get_session()

        self._additional_fixtures = []
        for fixture_cls in self.additional_fixtures:
            fixture = fixture_cls()
            self.useFixture(fixture)
            self._additional_fixtures.append(fixture)

    def tearDown(self):
        """Runs after each test method to tear down test environment."""
        super(TestCase, self).tearDown()
        # Reset any overridden flags
        CONF.reset()

        # Stop any timers
        for x in self.injected:
            try:
                x.stop()
            except AssertionError:
                pass

        # Delete attributes that don't start with _ so they don't pin
        # memory around unnecessarily for the duration of the test
        # suite
        for key in [k for k in self.__dict__.keys() if k[0] != '_']:
            del self.__dict__[key]

    def flags(self, group=None, **kw):
        """Override flag variables for a test."""
        for k, v in six.iteritems(kw):
            CONF.set_override(k, v, group)

    def path_get(self, project_file=None):
        """Get the absolute path to a file. Used for testing the API.

        :param project_file: File whose path to return. Default: None.
        :returns: path to the specified file, or path to project root.
        """
        root = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '..',
                                            '..',
                                            )
                               )
        if project_file:
            return os.path.join(root, project_file)
        else:
            return root
