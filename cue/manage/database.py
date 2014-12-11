# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Author: Endre Karlson <endre.karlson@hp.com>
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
#
# Copied: Designate
import os

from oslo.config import cfg
from oslo.db import options
from oslo.db.sqlalchemy.migration_cli import manager as migration_manager

from cue.manage import base


CONF = cfg.CONF


cfg.CONF.import_opt('connection', 'cue.db.api',
                    group='database')


def get_manager():
    alembic_path = os.path.join(os.path.dirname(__file__),
                                '..', 'db', 'sqlalchemy', 'alembic.ini')
    migrate_path = os.path.join(os.path.dirname(__file__),
                                '..', 'db', 'sqlalchemy', 'alembic')
    migration_config = {'alembic_ini_path': alembic_path,
                        'alembic_repo_path': migrate_path,
                        'db_url': CONF.database.connection}
    return migration_manager.MigrationManager(migration_config)


class DatabaseCommands(base.Commands):
    def __init__(self):
        options.set_defaults(CONF)

    def version(self):
        print("Version %s" % get_manager().version())

    @base.args('revision', nargs='?')
    def upgrade(self, revision):
        get_manager().upgrade(revision)

    @base.args('revision', nargs='?')
    def downgrade(self, revision):
        get_manager().downgrade(revision)

    @base.args('revision', nargs='?')
    def stamp(self, revision):
        get_manager().stamp(revision)

    @base.args('-m', '--message', dest='message')
    @base.args('--autogenerate', action='store_true')
    def revision(self, message, autogenerate):
        get_manager().revision(message=message, autogenerate=autogenerate)
