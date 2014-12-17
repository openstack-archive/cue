# Copyright 2011 VMware, Inc.
#    All Rights Reserved.
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
#
# Copied from Neutron
import uuid

from cue.db import api
from cue.db.sqlalchemy import models

from oslo.config import cfg
from oslo.db import options as db_options
from oslo.db.sqlalchemy import session
from oslo.utils import timeutils

CONF = cfg.CONF

CONF.register_opt(cfg.StrOpt('sqlite_db', default='cue.sqlite'))

db_options.set_defaults(
    cfg.CONF, connection='sqlite:///$state_path/$sqlite_db')

_FACADE = None


def _create_facade_lazily():
    global _FACADE

    if _FACADE is None:
        _FACADE = session.EngineFacade.from_config(cfg.CONF, sqlite_fk=True)

    return _FACADE


def get_engine():
    """Helper method to grab engine."""
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(autocommit=True, expire_on_commit=False):
    """Helper method to grab session."""
    facade = _create_facade_lazily()
    return facade.get_session(autocommit=autocommit,
                              expire_on_commit=expire_on_commit)


def get_backend():
    """The backend is this module itself."""
    return Connection()


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use.
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


class Connection(api.Connection):
    """SqlAlchemy connection implementation."""

    def __init__(self):
        pass

    def get_clusters(self, project_id):
        query = model_query(models.Cluster).filter_by(deleted=False)
                                                      #project_id=project_id)
        return query.all()

    def create_cluster(self, cluster_values):
        if not cluster_values.get('id'):
            cluster_values['id'] = str(uuid.uuid4())

        cluster_values['status'] = models.Status.BUILDING

        cluster = models.Cluster()
        cluster.update(cluster_values)

        node_values = {
            'cluster_id': cluster_values['id'],
            'flavor': cluster_values['flavor'],
            'volume_size': cluster_values['volume_size'],
            'status': models.Status.BUILDING,
        }

        db_session = get_session()
        with db_session.begin():
            cluster.save(db_session)
            db_session.flush()

            for i in range(cluster_values['size']):
                node = models.Node()
                node_id = str(uuid.uuid4())
                node_values['id'] = node_id
                node.update(node_values)
                node.save(db_session)

        return cluster

    def get_cluster_by_id(self, cluster_id):
        query = model_query(models.Cluster).filter_by(id=cluster_id)
        return query.one()

    def get_nodes_in_cluster(self, cluster_id):
        query = model_query(models.Node).filter_by(cluster_id=cluster_id)
        return query.all()

    def get_endpoints_in_node(self, node_id):
        query = model_query(models.Endpoint).filter_by(node_id=node_id)
        return query.all()

    def mark_cluster_as_delete(self, cluster_id):
        values = {'status': models.Status.DELETING,
                 'updated_at': timeutils.utcnow()}

        cluster_query = model_query(models.Cluster).filter_by(id=cluster_id)
        cluster_query.update(values)

        nodes_query = model_query(models.Node).filter_by(cluster_id=cluster_id)
        nodes_query.update(values)