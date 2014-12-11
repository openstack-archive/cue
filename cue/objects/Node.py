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


class Node(base.CueObject):

    dbapi = db_api.get_instance()

    fields = {
        'id': obj_utils.str_or_none,
        'cluster_id': obj_utils.str_or_none,
        'instance_id': obj_utils.str_or_none,
        'flavor': obj_utils.str_or_none,
        'status': obj_utils.str_or_none,
        'created_at': obj_utils.datetime_or_str_or_none,
        'updated_at': obj_utils.datetime_or_str_or_none,
        'deleted_at': obj_utils.datetime_or_str_or_none,
    }

    @staticmethod
    def _from_db_object(node, db_node):
        """Convert a database object to a universal node object."""
        for field in node.fields:
            node[field] = db_node[field]
        return node

    @classmethod
    def get_nodes(cls, cluster_id):
        """Returns a list of Node objects for specified cluster.

        :param cluster_id: UUID of the cluster.
        :returns: a list of :class:'Node' object.

        """
        db_nodes = cls.dbapi.get_nodes(cluster_id)

        return [Node._from_db_object(Node(), obj) for obj in db_nodes]
