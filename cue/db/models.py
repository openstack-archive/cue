import sqlalchemy as sa

from cue.db import base
from cue.db import types


CLUSTER_STATUSES = (
    'BUILDING',
    'ACTIVE',
    'DELETED',
    'ERROR',)


class Cluster(base.BASE, base.IdMixin, base.TimeMixin):
    __tablename__ = 'clusters'

    project_id = sa.Column(sa.String(36), nullable=False)
    nic = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(255), nullable=False)
    status = sa.Column(sa.String(50), sa.Enum(*CLUSTER_STATUSES))
    sa.Index("clusters_cluster_id_idx", "cluster_id", unique=True)


class Node(base.BASE, base.IdMixin, base.TimeMixin):
    __tablename__ = 'nodes'

    cluster_id = sa.Column(
        'cluster_id', types.UUID(),
        sa.ForeignKey('clusters.id'))
    node_id = sa.Column('node_id', sa.String(36), nullable=False)
    flavor = sa.Column('flavor', sa.SmallInteger(), nullable=False)
    sa.Index("nodes_id_idx", "id", unique=True)
    sa.Index("nodes_cluster_id_idx", "cluster_id", unique=False)


class EndpointTypes(base.BASE):
    __tablename__ = 'endpoint_types'

    type = sa.Column(sa.SmallInteger(), primary_key=True, autoincrement=False)
    description = sa.Column(sa.String(255), nullable=False)


class Endpoint(base.BASE):
    __tablename__ = 'endpoints'

    id = sa.Column(types.UUID(), sa.ForeignKey('nodes.id'), primary_key=True)
    uri = sa.Column(sa.String(255), nullable=False)
    type = sa.Column(sa.SmallInteger(),
                     sa.ForeignKey('endpoint_types.endpoint_type')),
    sa.Index("endpoints_id_idx", "id", unique=True)
