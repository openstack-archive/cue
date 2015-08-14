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

import collections

from cue.db.sqlalchemy import api as sql_api
from cue.db.sqlalchemy import base as sql_base

from oslo_config import cfg
from oslo_config import fixture as cfg_fixture
from oslotest import base

from cue.db.sqlalchemy import base as db_base
from cue.manage import database

conf = cfg.CONF


class MigrationFunctionalTests(base.BaseTestCase):

    cmd = None
    sorted_revision_list = None
    head = None

    def setUp(self):
        super(MigrationFunctionalTests, self).setUp()
        self.config_fixture = self.useFixture(cfg_fixture.Config(conf))
        self.config = self.config_fixture.config
        self.config_fixture.register_opt(cfg.StrOpt(
            'connection', default='sqlite://'))
        conf.set_override('connection', 'sqlite://', 'database')

        self.cmd = database.DatabaseCommands()

        # This Ordered Dictionary should be maintained to track each new
        # revision version that comes in.  The 'HEAD' revision is expected to
        # be in index len(sorted_revision_list)-1.
        self.sorted_revision_list = collections.OrderedDict([
            ('None', []),
            ('236f63c96b6a', ['clusters', 'endpoints', 'nodes']),
            ('3917e931a55a', ['clusters', 'endpoints', 'nodes', 'broker',
                              'broker_metadata']),
            ('244aa473e595', ['clusters', 'endpoints', 'nodes', 'broker',
                              'broker_metadata'])
        ])

        num_revisions = len(self.sorted_revision_list)
        self.head = list(self.sorted_revision_list.keys())[num_revisions - 1]

        engine = sql_api.get_engine()
        db_base.BASE.metadata.bind = engine

    def tearDown(self):
        super(MigrationFunctionalTests, self).tearDown()

    def test_upgrade(self):
        # This test will run incremental upgrades and compare the existing
        # tables against the 'expected' through the sorted_revision_list.

        tables = sql_base.BASE.metadata.sorted_tables

        for expected_version in self.sorted_revision_list:
            if expected_version is 'None':
                # Skipping if we are at the initial version since we
                # cannot upgrade to the initial.
                continue

            self.cmd.upgrade("+1")

            current_tables = []
            for t in tables:
                if t.exists():
                    current_tables.append(t.name)

            expected_tables = self.sorted_revision_list[expected_version]

            self.assertEqual(len(expected_tables), len(current_tables))

            for table in expected_tables:
                self.assertIn(table, current_tables, "Failed to find the " +
                              "expected table \'" + str(table) + "\' in the " +
                              "list of current tables.")

    def test_downgrade(self):
        # This test will run incremental downgrades and compare the existing
        # tables against the 'expected' through the sorted_revision_list.

        tables = sql_base.BASE.metadata.sorted_tables

        # Confirm initialization since this test isn't guaranteed to be the
        # first one ran after setUp().
        self.cmd.upgrade("head")

        for expected_version in reversed(self.sorted_revision_list):

            current_tables = []
            for t in tables:
                if t.exists():
                    current_tables.append(t.name)

            expected_tables = self.sorted_revision_list[expected_version]
            self.assertEqual(len(expected_tables), len(current_tables))

            for table in expected_tables:
                self.assertIn(table, current_tables)

            # Only downgrading if not at initial state
            if not expected_version == 'None':
                self.cmd.downgrade("-1")
