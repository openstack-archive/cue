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

from cue.common import policy
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
        'deleted': obj_utils.bool_or_none,
        'created_at': obj_utils.datetime_or_str_or_none,
        'updated_at': obj_utils.datetime_or_str_or_none,
        'deleted_at': obj_utils.datetime_or_str_or_none,
        'error_detail': obj_utils.str_or_none,
        'group_id': obj_utils.str_or_none,
    }

    @staticmethod
    def _from_db_object(cluster, db_cluster):
        """Convert a database object to a universal cluster object."""
        for field in cluster.fields:
            cluster[field] = db_cluster[field]
        return cluster

    def create(self, context):
        """Creates a new cluster.

        :param context: The request context

        """
        self['project_id'] = context.project_id
        cluster_changes = self.obj_get_changes()

        target = {'tenant_id': self['project_id']}
        policy.check('clusters:create', context, target)

        db_cluster = self.dbapi.create_cluster(context, cluster_changes)

        self._from_db_object(self, db_cluster)

    def update(self, context, cluster_id, *args, **kwargs):
        """Updates a database cluster object.

        :param context: The request context
        :param cluster_id:
        """
        cluster_changes = self.obj_get_changes()

        self.dbapi.update_cluster(context, cluster_changes,
                                  cluster_id, *args, **kwargs)

    @classmethod
    def get_clusters(cls, context):
        """Returns a list of Cluster objects for project_id.

        :param context: The request context.
        :returns: a list of :class:'Cluster' object.

        """
        target = {'tenant_id': context.tenant}
        policy.check('clusters:get', context, target)

        db_clusters = cls.dbapi.get_clusters(context)
        return [Cluster._from_db_object(Cluster(), obj) for obj in db_clusters]

    @classmethod
    def get_cluster_by_id(cls, context, cluster_id):
        """Returns a Cluster objects for specified cluster_id.

        :param context: The request context
        :param cluster_id: the cluster_id to retrieve
        :returns: a :class:'Cluster' object

        """
        db_cluster = cls.dbapi.get_cluster_by_id(context, cluster_id)

        target = {'tenant_id': db_cluster.project_id}
        policy.check("cluster:get", context, target)

        cluster = Cluster._from_db_object(Cluster(), db_cluster)

        return cluster

    @classmethod
    def update_cluster_deleting(cls, context, cluster_id):
        """Marks specified cluster to indicate deletion.

        :param context: The request context
        :param cluster_id: UUID of a cluster

        """
        db_cluster = cls.dbapi.get_cluster_by_id(context, cluster_id)
        target = {'tenant_id': db_cluster.project_id}
        policy.check("cluster:delete", context, target)
        cls.dbapi.update_cluster_deleting(context, cluster_id)
