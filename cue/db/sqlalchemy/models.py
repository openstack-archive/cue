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

import sqlalchemy as sa


class Status():
    BUILDING = 'BUILDING'
    ACTIVE = 'ACTIVE'
    DELETING = 'DELETING'
    DELETED = 'DELETED'
    ERROR = 'ERROR'


class Endpoint(base.BASE, base.IdMixin):
    __tablename__ = 'endpoints'

    node_id = sa.Column(types.UUID(), sa.ForeignKey('nodes.id'),
                        primary_key=True)
    uri = sa.Column(sa.String(255), nullable=False)
    type = sa.Column(sa.String(length=255), nullable=False)
    deleted = sa.Column(sa.Boolean(), nullable=False)
    sa.Index("endpoints_id_idx", "id", unique=True)
    sa.Index("endpoints_nodes_id_idx", "node_id", unique=False)

    @classmethod
    def add(cls, session, node_id, endpoint_type, uri):
        endpoint = {
            "node_id": node_id,
            "uri": uri,
            "type": endpoint_type,
            "deleted": False
        }

        return super(Endpoint, cls).create(session, **endpoint)


class Node(base.BASE, base.IdMixin, base.TimeMixin):
    __tablename__ = 'nodes'

    cluster_id = sa.Column(
        'cluster_id', types.UUID(),
        sa.ForeignKey('clusters.id'), nullable=False)
    flavor = sa.Column(sa.String(36), nullable=False)
    instance_id = sa.Column(sa.String(36), nullable=True)
    status = sa.Column(sa.String(50), nullable=False)
    volume_size = sa.Column(sa.Integer(), nullable=False)
    deleted = sa.Column(sa.Boolean(), default=False, nullable=False)
    sa.Index("nodes_id_idx", "id", unique=True)
    sa.Index("nodes_cluster_id_idx", "cluster_id", unique=False)

    @classmethod
    def add(cls, session, cluster_id, flavor, vol_size):
        node = {
            "cluster_id": cluster_id,
            "flavor": flavor,
            "volume_size": vol_size,
            "deleted": False,
            "status": Status.BUILDING
        }

        return super(Node, cls).create(session, **node)

    @classmethod
    def delete(cls, session, node_id):
        super(Node, cls).update(session, id=node_id, status=Status.DELETING)


class Cluster(base.BASE, base.IdMixin, base.TimeMixin):
    __tablename__ = 'clusters'

    project_id = sa.Column(sa.String(36), nullable=False)
    nic = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(255), nullable=False)
    status = sa.Column(sa.String(50), nullable=False)
    volume_size = sa.Column(sa.Integer(), nullable=False)
    deleted = sa.Column(sa.Boolean(), default=False, nullable=False)
    sa.Index("clusters_cluster_id_idx", "cluster_id", unique=True)

    @classmethod
    def add(cls, session, cluster_id, project_id, name, nic, vol_size):
        cluster = {
            "id": cluster_id,
            "project_id": project_id,
            "name": name,
            "nic": nic,
            "volume_size": vol_size,
            "deleted": False,
            "status": Status.BUILDING
        }

        return super(Cluster, cls).create(session, **cluster)

    @classmethod
    def delete(cls, session, cluster_id):
        super(Cluster, cls).update(session, id=cluster_id,
                                   status=Status.DELETING)