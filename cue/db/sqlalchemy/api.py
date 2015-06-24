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

from cue.common import exception
from cue.common.i18n import _  # noqa
from cue.db import api
from cue.db.sqlalchemy import models

from oslo_config import cfg
from oslo_db import exception as db_exception
from oslo_db import options as db_options
from oslo_db.sqlalchemy import session
from oslo_utils import timeutils
from sqlalchemy.orm import exc as sql_exception

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


def model_query(context, model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """
    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)

    read_deleted = kwargs.get('read_deleted', False)
    project_only = kwargs.get('project_only', True)

    if not read_deleted:
        query = query.filter_by(deleted=False)

    if project_only:
        # filter by project_id
        if hasattr(model, 'project_id'):
            query = query.filter_by(project_id=context.project_id)

    return query


def soft_delete(record_values):
        """Mark this object as deleted."""
        record_values['deleted'] = True
        record_values['deleted_at'] = timeutils.utcnow()


class Connection(api.Connection):
    """SqlAlchemy connection implementation."""

    def __init__(self):
        pass

    def get_clusters(self, context):
        query = model_query(context, models.Cluster)
        return query.all()

    def create_cluster(self, context, cluster_values):
        if not cluster_values.get('id'):
            cluster_values['id'] = str(uuid.uuid4())

        cluster_values['status'] = models.Status.BUILDING
        cluster = models.Cluster()
        cluster.update(cluster_values)

        node_values = {
            'cluster_id': cluster_values['id'],
            'flavor': cluster_values['flavor'],
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

    def update_cluster(self, context, cluster_values, cluster_id):
        cluster_query = (model_query(context, models.Cluster)
            .filter_by(id=cluster_id))

        # if status is set to deleted, soft delete this cluster record
        if ('status' in cluster_values) and (
                    cluster_values['status'] == models.Status.DELETED):
            soft_delete(cluster_values)

        cluster_query.update(cluster_values)

    def get_cluster_by_id(self, context, cluster_id):
        query = model_query(context, models.Cluster).filter_by(id=cluster_id)
        try:
            cluster = query.one()
        except db_exception.DBError:
            # Todo(dagnello): User input will be validated from REST API and
            # not from DB transactions.
            raise exception.Invalid(_("badly formed cluster_id UUID string"))
        except sql_exception.NoResultFound:
            raise exception.NotFound(_("Cluster was not found"))

        return cluster

    def get_nodes_in_cluster(self, context, cluster_id):
        query = (model_query(context, models.Node)
            .filter_by(cluster_id=cluster_id))
        # No need to catch user-derived exceptions around not found or badly
        # formed UUIDs if these happen, they should be classified as internal
        # server errors since the user is not able to access nodes directly.
        return query.all()

    def get_node_by_id(self, context, node_id):
        query = model_query(context, models.Node).filter_by(id=node_id)
        return query.one()

    def update_node(self, context, node_values, node_id):
        node_query = (model_query(context, models.Node).filter_by(id=node_id))

        # if status is set to deleted, soft delete this node record
        if ('status' in node_values) and (
            node_values['status'] == models.Status.DELETED):
            soft_delete(node_values)

        node_query.update(node_values)

    def get_endpoints_in_node(self, context, node_id):
        query = model_query(context, models.Endpoint).filter_by(
            node_id=node_id)
        # No need to catch user-derived exceptions for same reason as above
        return query.all()

    def create_endpoint(self, context, endpoint_values):
        if not endpoint_values.get('id'):
            endpoint_values['id'] = str(uuid.uuid4())

        endpoint = models.Endpoint()
        endpoint.update(endpoint_values)

        db_session = get_session()
        endpoint.save(db_session)

        return endpoint

    def get_endpoint_by_id(self, context, endpoint_id):
        query = model_query(context, models.Endpoint).filter_by(id=endpoint_id)
        return query.one()

    def update_endpoints_by_node_id(self, context, endpoint_values, node_id):
        endpoints_query = model_query(context, models.Endpoint).filter_by(
            node_id=node_id)

        # if delete flag is set, we just want to delete these records instead
        if 'deleted' in endpoint_values and endpoint_values['deleted']:
            endpoints_query.delete()
        else:
            endpoints_query.update(endpoint_values)

    def update_cluster_deleting(self, context, cluster_id):
        values = {'status': models.Status.DELETING}

        cluster_query = (model_query(context, models.Cluster)
            .filter_by(id=cluster_id))

        try:
            cluster_query.one()
        except db_exception.DBError:
            # Todo(dagnello): User input will be validated from REST API and
            # not from DB transactions.
            raise exception.Invalid(_("badly formed cluster_id UUID string"))
        except sql_exception.NoResultFound:
            raise exception.NotFound(_("Cluster was not found"))

        db_session = get_session()

        with db_session.begin():
            cluster_query.update(values)
            nodes_query = model_query(context, models.Node).filter_by(
                cluster_id=cluster_id)
            nodes_query.update(values)

    def create_broker(self, context, broker_values):

        broker = models.Broker()
        broker.update(broker_values)

        db_session = get_session()
        broker.save(db_session)
        return broker

    def get_brokers(self, context):
        query = model_query(context, models.Broker)
        return query.all()

    def delete_broker(self, context, broker_id):

        broker_query = (model_query(context, models.Broker)
                        .filter_by(id=broker_id))

        broker_value = {}
        soft_delete(broker_value)
        broker_query.update(broker_value)

    def update_broker(self, context, broker_id, broker_value):

        broker_query = (model_query(context, models.Broker)
                        .filter_by(id=broker_id))

        broker_query.update(broker_value)

    def create_broker_metadata(self, context, metadata_values):

        broker_query = (model_query(context, models.Broker)
                        .filter_by(id=metadata_values['broker_id']))
        try:
            # check to see if the broker_id exists
            broker_query.one()
            broker_metadata = models.BrokerMetadata()
            broker_metadata.update(metadata_values)
            db_session = get_session()
            broker_metadata.save(db_session)
        except db_exception.DBError:
            raise exception.Invalid(_("Badly formed broker_id UUID string"))
        except sql_exception.NoResultFound:
            raise exception.NotFound(_("Broker was not found"))

        return broker_metadata

    def get_broker_metadata_by_broker_id(self, context, broker_id):

        query = model_query(context, models.BrokerMetadata).filter_by(
            broker_id=broker_id)
        broker_metadata = query.all()

        return broker_metadata

    def delete_broker_metadata(self, context, broker_metadata_id):

        query = (model_query(context, models.BrokerMetadata).filter_by(
            id=broker_metadata_id))

        broker_value = {}
        soft_delete(broker_value)
        query.update(broker_value)

    def get_image_id_by_broker_name(self, context, broker_name):

        broker_query = model_query(context, models.Broker).filter_by(
            active=True).filter_by(name=broker_name)

        try:
            selected_broker_id = broker_query.one().id

            # select the recently created image id
            metadata_query = (model_query(context, models.BrokerMetadata)
                              .filter_by(key='IMAGE')
                              .filter_by(broker_id=selected_broker_id)
                              .order_by((models.BrokerMetadata.created_at.desc(
                              ))).limit(1))
            selected_image = metadata_query.one()

        except sql_exception.NoResultFound:
            raise exception.NotFound(_("Broker was not found"))

        image_id = selected_image['value']
        return image_id