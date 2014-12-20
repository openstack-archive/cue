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

from cue.db import api as db_api
from cue.objects import base
from cue.objects import utils as obj_utils


class Cluster(base.CueObject):

    dbapi = db_api.get_instance()

    fields = {
        'id': obj_utils.str_or_none,
        'network_id': obj_utils.str_or_none,
        'project_id': obj_utils.str_or_none,
        'name': obj_utils.str_or_none,
        'status': obj_utils.str_or_none,
        'flavor': obj_utils.str_or_none,
        'size': obj_utils.int_or_none,
        'volume_size': obj_utils.int_or_none,
        'created_at': obj_utils.datetime_or_str_or_none,
        'updated_at': obj_utils.datetime_or_str_or_none,
        'deleted_at': obj_utils.datetime_or_str_or_none,
    }

    @staticmethod
    def _from_db_object(cluster, db_cluster):
        """Convert a database object to a universal cluster object."""
        for field in cluster.fields:
            cluster[field] = db_cluster[field]
        return cluster

    def create_cluster(self, project_id):
        """Creates a new cluster.

        :param project_id: The project id the cluster resides in.
        :param flavor: The required flavor for nodes in this cluster.
        :param number_of_nodes: The number of nodes in this cluster.

        """
        self['project_id'] = project_id
        cluster_changes = self.obj_get_changes()

        db_cluster = self.dbapi.create_cluster(cluster_changes)

        self._from_db_object(self, db_cluster)

    @classmethod
    def get_clusters(cls, project_id):
        """Returns a list of Cluster objects for specified project_id.

        :param project_id: UUID of a project/tenant.
        :returns: a list of :class:'Cluster' object.

        """
        db_clusters = cls.dbapi.get_clusters(project_id)
        return [Cluster._from_db_object(Cluster(), obj) for obj in db_clusters]

    @classmethod
    def get_cluster_by_id(cls, cluster_id):
        """Returns a Cluster objects for specified cluster_id.

        :param cluster_id: UUID of a cluster.
        :returns: a :class:'Cluster' object.

        """
        db_cluster = cls.dbapi.get_cluster_by_id(cluster_id)
        cluster = Cluster._from_db_object(Cluster(), db_cluster)
        return cluster

    @classmethod
    def mark_cluster_as_delete(cls, cluster_id):
        """Marks specified cluster to indicate deletion.

        :param cluster_id: UUID of a cluster.

        """
        cls.dbapi.mark_cluster_as_delete(cluster_id)