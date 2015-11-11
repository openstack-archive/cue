# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Author: Endre Karlson <endre.karlson@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from cue.db.sqlalchemy import base
from cue.db.sqlalchemy import types

from oslo_db.sqlalchemy import models
import sqlalchemy as sa


class Status():
    BUILDING = 'BUILDING'
    ACTIVE = 'ACTIVE'
    DELETING = 'DELETING'
    DELETED = 'DELETED'
    ERROR = 'ERROR'
    DOWN = 'DOWN'


class MetadataKey():
    IMAGE = 'IMAGE'
    SEC_GROUP = 'SEC_GROUP'


class Endpoint(base.BASE, base.IdMixin):
    __tablename__ = 'endpoints'

    node_id = sa.Column(types.UUID(), sa.ForeignKey('nodes.id'),
                        primary_key=True)
    uri = sa.Column(sa.String(255), nullable=False)
    type = sa.Column(sa.String(length=255), nullable=False)
    deleted = sa.Column(sa.Boolean(), default=False, nullable=False)
    sa.Index("endpoints_id_idx", "id", unique=True)
    sa.Index("endpoints_nodes_id_idx", "node_id", unique=False)


class Node(base.BASE, base.IdMixin, models.TimestampMixin,
           base.SoftDeleteMixin):
    __tablename__ = 'nodes'

    cluster_id = sa.Column(
        'cluster_id', types.UUID(),
        sa.ForeignKey('clusters.id'), nullable=False)
    flavor = sa.Column(sa.String(36), nullable=False)
    instance_id = sa.Column(sa.String(36), nullable=True)
    status = sa.Column(sa.String(50), nullable=False)
    management_ip = sa.Column(sa.String(45), nullable=True)
    sa.Index("nodes_id_idx", "id", unique=True)
    sa.Index("nodes_cluster_id_idx", "cluster_id", unique=False)


class Cluster(base.BASE, base.IdMixin, models.TimestampMixin,
              base.SoftDeleteMixin):
    __tablename__ = 'clusters'

    project_id = sa.Column(sa.String(36), nullable=False)
    network_id = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(255), nullable=False)
    status = sa.Column(sa.String(50), nullable=False)
    flavor = sa.Column(sa.String(50), nullable=False)
    size = sa.Column(sa.Integer(), default=1, nullable=False)
    volume_size = sa.Column(sa.Integer(), nullable=True)
    error_detail = sa.Column(sa.Text(), nullable=True)
    group_id = sa.Column(types.UUID(), nullable=True)
    sa.Index("clusters_cluster_id_idx", "cluster_id", unique=True)


class Broker(base.BASE, base.IdMixin, models.TimestampMixin,
             base.SoftDeleteMixin):
    __tablename__ = 'broker'

    name = sa.Column(sa.String(255), nullable=False)
    active = sa.Column(sa.Boolean(), default=False, nullable=False)
    sa.Index("broker_id_idx", "id", unique=True)


class BrokerMetadata(base.BASE, base.IdMixin, models.TimestampMixin,
                     base.SoftDeleteMixin):
    __tablename__ = 'broker_metadata'

    broker_id = sa.Column(
        'broker_id', types.UUID(),
        sa.ForeignKey('broker.id'), nullable=False)
    key = sa.Column(sa.String(255), nullable=False)
    value = sa.Column(sa.String(255), nullable=False)
    sa.Index("brokerMetadata_id_idx", "id", unique=True)
    sa.Index("brokerMetadata_broker_id_idx", "broker_id", unique=False)