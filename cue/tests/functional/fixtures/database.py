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

import os
import shutil

import fixtures
from oslo.config import cfg

from cue.db.sqlalchemy import base as db_base


CONF = cfg.CONF


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