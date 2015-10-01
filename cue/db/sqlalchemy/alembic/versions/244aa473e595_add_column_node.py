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
"""Add management_ip column in node

Revision ID: 244aa473e595
Revises: 3917e931a55a
Create Date: 2015-10-01 12:02:57.273927

"""

# revision identifiers, used by Alembic.
revision = '244aa473e595'
down_revision = '3917e931a55a'

from alembic import op
from oslo_config import cfg
import sqlalchemy as sa


def upgrade():
    op.add_column('nodes', sa.Column('management_ip', sa.String(length=45)))


def downgrade():
    db_connection = cfg.CONF.database.connection
    if db_connection != "sqlite://":  # noqa
        op.drop_column('nodes', 'management_ip')