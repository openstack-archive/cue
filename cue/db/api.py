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

from oslo.config import cfg
from oslo.db import api as db_api
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
    def get_clusters(self, context):
        """Returns a list of Cluster objects for specified project_id.

        :param context: request context object
        :returns: a list of :class:'Cluster' object.

        """

    @abc.abstractmethod
    def create_cluster(self, context, cluster_values):
        """Creates a new cluster.

        :param context: request context object
        :param cluster_values: Dictionary of several required items.

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
    def get_cluster_by_id(self, context, cluster_id):
        """Returns a Cluster objects for specified cluster_id.

        :param context: request context object
        :param cluster_id: UUID of a cluster.
        :returns: a :class:'Cluster' object.
        """

    @abc.abstractmethod
    def get_nodes_in_cluster(self, context, cluster_id):
        """Returns a list of Node objects for specified cluster.

        :param context: request context object
        :param cluster_id: UUID of the cluster.
        :returns: a list of :class:'Node' object.

        """

    @abc.abstractmethod
    def get_node_by_id(self, context, node_id):
        """Returns a node for the specified node_id.

        :param context: request context object
        :param node_id: UUID of the node.
        :returns: a :class:'Node' object.

        """

    @abc.abstractmethod
    def update_node_status(self, context, node_id, status):
        """Updates status for a node for the specified status.

        :param context: request context object
        :param node_id: UUID of the node.
        :param status: new status of the node.
        :returns: a :class:'Node' object.

        """

    @abc.abstractmethod
    def get_endpoints_in_node(self, context, node_id):
        """Returns a list of Endpoint objects for specified node.

        :param context: request context object
        :param node_id: UUID of the node.
        :returns: a list of :class:'Endpoint' object.

        """

    @abc.abstractmethod
    def get_endpoint_by_id(self, context, endpoint_id):
        """Returns an endpoint for the specified endpoint_id.

        :param context: request context object
        :param endpoint_id: UUID of the endpoint.
        :returns: a :class:'Endpoint' object.

        """

    @abc.abstractmethod
    def update_cluster_status(self, context, cluster_id, status):
        """Updates cluster status to indicated status.

        :param context: request context object
        :param cluster_id: UUID of a cluster.
        :param status: New cluster status

        """

    @abc.abstractmethod
    def update_cluster_deleting(self, context, cluster_id):
        """Marks specified cluster to indicate deletion.

        :param context: request context object
        :param cluster_id: UUID of a cluster.

        """