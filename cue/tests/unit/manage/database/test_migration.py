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
# Copyright [2015] Hewlett-Packard Development Company, L.P.
# limitations under the License.


import mock
from oslo_config import cfg
from oslotest import base as oslo_base

from cue.manage import database as cue_db

CONF = cfg.CONF


class TestMigration(oslo_base.BaseTestCase):

    cue_manage_database = None

    def setUp(self):
        super(TestMigration, self).setUp()

        CONF.set_override("connection", "sqlite://", group="database")
        self.cue_manage_database = cue_db.DatabaseCommands()

    @mock.patch('oslo_db.sqlalchemy.migration_cli.manager.'
                'MigrationManager.revision')
    def test_revision(self, mock_oslo_revision):
        """Verifies cue-manage database revision call hits oslo."""

        self.cue_manage_database.revision('test_migration', False)
        mock_oslo_revision.assert_called_once_with(
            message='test_migration', autogenerate=False)

    @mock.patch('oslo_db.sqlalchemy.migration_cli.manager.'
                'MigrationManager.upgrade')
    def test_upgrade(self, mock_oslo_upgrade):
        """Verifies cue-manage database upgrade call."""

        self.cue_manage_database.upgrade(None)
        mock_oslo_upgrade.assert_called_once_with(None)

    @mock.patch('oslo_db.sqlalchemy.migration_cli.manager.'
                'MigrationManager.downgrade')
    def test_downgrade(self, mock_oslo_downgrade):
        """Verifies cue-manage database downgrade call."""

        self.cue_manage_database.downgrade(None)
        mock_oslo_downgrade.assert_called_once_with(None)

    @mock.patch('oslo_db.sqlalchemy.migration_cli.manager.'
                'MigrationManager.version')
    def test_version(self, mock_oslo_version):
        """Verifies cue-manage database version call."""

        self.cue_manage_database.version()
        mock_oslo_version.assert_called_once_with()

    @mock.patch('oslo_db.sqlalchemy.migration_cli.manager.'
                'MigrationManager.stamp')
    def test_stamp(self, mock_oslo_stamp):
        """Verifies cue-manage database stamp call."""

        self.cue_manage_database.stamp(None)
        mock_oslo_stamp.assert_called_once_with(None)
