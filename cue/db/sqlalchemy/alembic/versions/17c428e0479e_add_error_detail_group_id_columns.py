# -*- encoding: utf-8 -*-
#
# Copyright 2015 Hewlett-Packard Development Company, L.P.
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
"""add error_detail and group_id column in clusters

Revision ID: 17c428e0479e
Revises: 244aa473e595
Create Date: 2015-11-11 12:01:10.769280

"""

# revision identifiers, used by Alembic.
revision = '17c428e0479e'
down_revision = '244aa473e595'

from cue.db.sqlalchemy import types

from alembic import op
from oslo_config import cfg
import sqlalchemy as sa


def upgrade():
     op.add_column('clusters', sa.Column('error_detail', sa.Text(),
                                         nullable=True))
     op.add_column('clusters', sa.Column('group_id', types.UUID(),
                                         nullable=True))


def downgrade():
    db_connection = cfg.CONF.database.connection
    if db_connection != "sqlite://":  # pragma: nocover
        op.drop_column('clusters', 'error_detail')
        op.drop_column('clusters', 'group_id')