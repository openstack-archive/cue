# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Authors: Davide Agnello <davide.agnello@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Copyright [2014] Hewlett-Packard Development Company, L.P.
# limitations under the License.
"""
Base classes for storage engines
"""

import abc

from oslo_config import cfg
from oslo_db import api as db_api
import six

_BACKEND_MAPPING = {'sqlalchemy': 'cue.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING,
                                lazy=True)


def get_instance():
    """Return a DB API instance."""
    return IMPL


@six.add_metaclass(abc.ABCMeta)
class Connection(object):
    """Base class for storage system connections."""

    @abc.abstractmethod
    def __init__(self):
        """Constructor."""

    @abc.abstractmethod
    def get_clusters(self, context, *args, **kwargs):
        """Returns a list of Cluster objects for specified project_id.

        :param context: request context object
        :returns: a list of :class:'Cluster' object

        """

    @abc.abstractmethod
    def create_cluster(self, context, cluster_values):
        """Creates a new cluster.

        :param context: request context object
        :param cluster_values: Dictionary of several required items

               ::

               {
                'network_id': obj_utils.str_or_none,
                'project_id': obj_utils.str_or_none,
                'name': obj_utils.str_or_none,
                'flavor': obj_utils.str_or_none,
                'size': obj_utils.int_or_none,
                'volume_size': obj_utils.int_or_none,
               }

        """

    @abc.abstractmethod
    def update_cluster(self, context, cluster_values, cluster_id):
        """Updates values in a cluster record indicated by cluster_id

        :param context: request context object
        :param cluster_values: Dictionary of cluster values to update
        :param cluster_id: UUID of a cluster

        """

    @abc.abstractmethod
    def get_cluster_by_id(self, context, cluster_id):
        """Returns a Cluster objects for specified cluster_id.

        :param context: request context object
        :param cluster_id: UUID of a cluster
        :returns: a :class:'Cluster' object

        """

    @abc.abstractmethod
    def get_nodes_in_cluster(self, context, cluster_id):
        """Returns a list of Node objects for specified cluster.

        :param context: request context object
        :param cluster_id: UUID of the cluster
        :returns: a list of :class:'Node' object

        """

    @abc.abstractmethod
    def get_node_by_id(self, context, node_id):
        """Returns a node for the specified node_id.

        :param context: request context object
        :param node_id: UUID of the node
        :returns: a :class:'Node' object

        """

    @abc.abstractmethod
    def update_node(self, context, node_values, node_id):
        """Updates values in a node record indicated by node_id

        :param context: request context object
        :param node_values: Dictionary of node values to update
        :param node_id:
        :return:
        """

    @abc.abstractmethod
    def get_endpoints_in_node(self, context, node_id):
        """Returns a list of Endpoint objects for specified node.

        :param context: request context object
        :param node_id: UUID of the node
        :returns: a list of :class:'Endpoint' object

        """

    @abc.abstractmethod
    def create_endpoint(self, context, endpoint_values):
        """Creates a new endpoint.

        :param context: request context object
        :param endpoint_values: Dictionary of several required items

               ::

               {
                'id': obj_utils.str_or_none,
                'node_id': obj_utils.str_or_none,
                'uri': obj_utils.str_or_none,
                'type': obj_utils.str_or_none,
               }

        """

    @abc.abstractmethod
    def get_endpoint_by_id(self, context, endpoint_id):
        """Returns an endpoint for the specified endpoint_id.

        :param context: request context object
        :param endpoint_id: UUID of the endpoint
        :returns: a :class:'Endpoint' object

        """

    @abc.abstractmethod
    def update_endpoints_by_node_id(self, context, endpoint_values, node_id):
        """Updates values in all endpoints belonging to a specific node

        :param context: request context object
        :param endpoint_values: Dictionary of endpoint values to update
        :param node_id: node id to query endpoints by
        :return:
        """

    @abc.abstractmethod
    def update_cluster_deleting(self, context, cluster_id):
        """Marks specified cluster to indicate deletion.

        :param context: request context object
        :param cluster_id: UUID of a cluster

        """

    @abc.abstractmethod
    def create_broker(self, context, broker_values):
        """Creates a new broker.

       :param context: request context object
       :param broker_values: Dictionary of several required items
               ::

               {
                'type': obj_utils.str_or_none,
                'active_status': obj_utils.bool_or_none
               }
         """

    @abc.abstractmethod
    def get_brokers(self, context):
        """Returns a list of Broker objects.

        :param context: request context object
        :returns: a list of :class:'Broker' object

        """

    @abc.abstractmethod
    def delete_broker(self, context, broker_id):
        """Deletes a Broker object for specified broker_id.

        :param context: request context object
        :param broker_id: UUID of a broker

        """

    @abc.abstractmethod
    def update_broker(self, context, broker_id, broker_value):
        """Updates a Broker type/status for specified broker_id.

        :param context: request context object
        :param broker_id: UUID of a broker
        :param broker_value: Dictionary of attribute values to be updated

        """

    @abc.abstractmethod
    def create_broker_metadata(self, context, metadata_values):
        """Creates a new broker metadata.

       :param context: request context object
       :param metadata_values: Dictionary of several required items
               ::

               {
                'broker_id': UUID of a broker,
                'key': obj_utils.str_or_none,
                'value': obj_utils.str_or_none
               }
         """

    @abc.abstractmethod
    def get_broker_metadata_by_broker_id(self, context, broker_id):
        """Returns a list of BrokerMetadata objects for specified broker_id.

        :param context: request context object
        :param broker_id: UUID of a broker
        :returns: a list of :class:'BrokerMetadata' object

        """
    @abc.abstractmethod
    def delete_broker_metadata(self, context, broker_metadata_id):
        """Deletes a BrokerMetadata object for specified broker_id.

        :param context: request context object
        :param broker_metadata_id: UUID of a broker metadata

        """
    @abc.abstractmethod
    def get_image_id_by_broker_name(self, context, broker_name):
        """Returns a image_id for the broker

        :param context: request context object
        :param: broker name

        """