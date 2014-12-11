#    Copyright 2011 VMware, Inc.
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
from cue.db import api
from cue.db.sqlalchemy import models

from oslo.config import cfg
from oslo.db import options as db_options
from oslo.db.sqlalchemy import session

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


class Connection(api.Connection):
    """SqlAlchemy connection implementation."""

    def __init__(self):
        pass

    def get_clusters(self, project_id):
        db_session = get_session()
        db_filter = {
            # TODO(dagnello): update project_id accordingly when enabled
            #'project_id': project_id,
            'deleted': False,
        }
        return models.Cluster.get_all(db_session, **db_filter)

    def create_cluster(self, cluster_values, flavor, number_of_nodes):
        db_session = get_session()

        cluster_ref = models.Cluster.add(db_session, cluster_values.project_id,
                                         cluster_values.name,
                                         cluster_values.nic,
                                         cluster_values.volume_size)

        for i in range(number_of_nodes):
            models.Node.add(db_session, cluster_ref.id, flavor,
                            cluster_values['volume_size'])

        return cluster_ref

    def get_cluster(self, cluster_id):
        db_session = get_session()
        return models.Cluster.get(db_session, id=cluster_id)

    def get_nodes(self, cluster_id):
        db_session = get_session()

        return models.Node.get_all(db_session, cluster_id=cluster_id)

    def get_endpoints(self, node_id):
        db_session = get_session()

        node_endpoint_ref = models.Endpoint.get_all(db_session,
                                                    node_id=node_id)

        return node_endpoint_ref

    def mark_as_delete_cluster(self, cluster_id):
        db_session = get_session()

        cluster_node_ref = models.Node.get_all(db_session,
                                               cluster_id=cluster_id)
        models.Cluster.delete(db_session, cluster_id)

        for node in cluster_node_ref:
            models.Node.delete(db_session, node.id)