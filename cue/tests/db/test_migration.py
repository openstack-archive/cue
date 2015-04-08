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

import mock

from cue.manage import database as cue_db
from cue.tests import base


@mock.patch('oslo.db.sqlalchemy.migration_cli.manager.'
            'MigrationManager.revision')
class MigrationTests(base.TestCase):

    def test_migration(self, mock_cue_manage_database):
        """Verifies cue-master database revision call hits oslo."""

        cue_manage_database = cue_db.DatabaseCommands()
        cue_manage_database.revision('test_migration', False)

        mock_cue_manage_database.assert_called_once_with(
            message='test_migration', autogenerate=False)