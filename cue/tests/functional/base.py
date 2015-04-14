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

import os

from oslo.config import cfg
from oslotest import base
import six

from cue.common import context as cue_context
from cue.db.sqlalchemy import api as db_api
from cue.manage import database
from cue.tests.functional.fixtures import database as database_fixture
from cue.tests.functional.fixtures import policy


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


class FunctionalTestCase(base.BaseTestCase):
    """Test case base class for all unit tests."""

    additional_fixtures = []
    #todo(dagnello): add enable_fixures as a configurable parameters for
    #running tests.
    enable_fixtures = True

    def setUp(self):
        """Run before each test method to initialize test environment."""
        super(FunctionalTestCase, self).setUp()

        self.context = self.get_context()
        self.flags(state_path='/tmp')
        self.flags(connection="sqlite://", group="database")

        self._include_default_fixtures()

        if self.enable_fixtures:
            for fixture_cls in self.additional_fixtures:
                fixture = fixture_cls()
                self.useFixture(fixture)

    def get_context(self, **kwargs):
        auth_token = kwargs.get('auth_token', "auth_xxx")
        user = kwargs.get("user", "user")
        tenant = kwargs.get("tenant", "tenant-a")
        return cue_context.RequestContext(auth_token=auth_token,
                                          user=user,
                                          tenant=tenant,
                                          )

    def tearDown(self):
        """Runs after each test method to tear down test environment."""
        super(FunctionalTestCase, self).tearDown()
        # Reset any overridden flags
        CONF.reset()

        # Delete attributes that don't start with _ so they don't pin
        # memory around unnecessarily for the duration of the test
        # suite
        for key in [k for k in self.__dict__.keys() if k[0] != '_']:
            del self.__dict__[key]

    def _include_default_fixtures(self):
        global _DB_CACHE
        if not _DB_CACHE:
            DB_CACHE = database_fixture.Database(
                db_api,
                database.get_manager(),
                sql_connection=CONF.database.connection,
                sqlite_db=CONF.sqlite_db,
                sqlite_clean_db=CONF.sqlite_clean_db,
            )
        self.useFixture(DB_CACHE)
        self.useFixture(policy.PolicyFixture())

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
