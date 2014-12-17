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
    def get_clusters(self, project_id):
        """Returns a list of Cluster objects for specified project_id.

        :param project_id: UUID of a project/tenant.
        :returns: a list of :class:'Cluster' object.

        """

    @abc.abstractmethod
    def create_cluster(self, cluster_values, flavor, number_of_nodes):
        """Creates a new cluster.

        :param cluster_values: Dictionary of several required items.

               ::

               {
                'project_id': obj_utils.str_or_none,
                'name': obj_utils.str_or_none,
                'nic': obj_utils.str_or_none,
                'volume_size': obj_utils.int_or_none,
               }
        :param flavor: The required flavor for nodes in this cluster.
        :param number_of_nodes: The number of nodes in this cluster.

        """

    @abc.abstractmethod
    def get_cluster_by_id(self, cluster_id):
        """Returns a Cluster objects for specified cluster_id.

        :param cluster_id: UUID of a cluster.
        :returns: a :class:'Cluster' object.

        """

    @abc.abstractmethod
    def get_nodes_in_cluster(self, cluster_id):
        """Returns a list of Node objects for specified cluster.

        :param cluster_id: UUID of the cluster.
        :returns: a list of :class:'Node' object.

        """

    @abc.abstractmethod
    def get_endpoints_in_node(self, node_id):
        """Returns a list of Endpoint objects for specified node.

        :param node_id: UUID of the node.
        :returns: a list of :class:'Endpoint' object.

        """

    @abc.abstractmethod
    def mark_cluster_as_delete(self, cluster_id):
        """Marks specified cluster to indicate deletion.

        :param cluster_id: UUID of a cluster.

        """