# Copyright 2015 Hewlett-Packard Development Company, L.P.
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
Tests for cue objects.
"""
from oslo.utils import timeutils

from cue.db.sqlalchemy import models
from cue import objects
from cue.tests.unit import base
from cue.tests import utils as test_utils


class CueObjectsTest(base.UnitTestCase):

    def get_test_cluster(self):
        return {
            'id': '1be26c0b-03f2-4d2e-ae87-c02d7f33c781',
            'project_id': '1234567890',
            'name': 'sample_cluster',
            'network_id': '3dc26c0b-03f2-4d2e-ae87-c02d7f33c788',
            'status': 'BUILDING',
            'flavor': 'flavor1',
            'size': 1,
            'volume_size': 10,
            'deleted': False,
            'created_at': timeutils.utcnow(),
            'updated_at': timeutils.utcnow(),
            'deleted_at': None,
        }

    def test_cluster_object_to_dict(self):
        """test conversion of Cluster object to dict using as_dict."""
        cluster = self.get_test_cluster()
        cluster_obj = objects.Cluster(**cluster)
        cluster_dict = cluster_obj.as_dict()
        test_utils.validate_cluster_values(self, cluster, cluster_dict)

    def test_cluster_object_to_dict_with_invalid_field(self):
        """test conversion of Cluster object to dict with an invalid field."""
        cluster = self.get_test_cluster()
        cluster_obj = objects.Cluster(**cluster)
        cluster_obj['endpoint'] = '10.0.0.4:5672'
        cluster_dict = cluster_obj.as_dict()
        self.assertRaises(KeyError, lambda: cluster_dict['endpoint'])

    def test_get_object_changes(self):
        """test Cluster object changes by setting a valid field."""
        cluster_obj = objects.Cluster()
        cluster_obj['status'] = models.Status.DELETING
        cluster_changes_dict = cluster_obj.obj_get_changes()
        # check the changed field
        self.assertEqual(models.Status.DELETING,
                         cluster_changes_dict['status'])
        # check for an unchanged field
        self.assertRaises(KeyError, lambda: cluster_changes_dict['name'])

    def test_get_object_changes_with_invalid_field(self):
        """test Cluster object changes by setting an invalid field."""
        cluster_obj = objects.Cluster()
        cluster_obj['endpoint'] = '10.0.0.4:5672'
        cluster_dict = cluster_obj.obj_get_changes()
        self.assertFalse(bool(cluster_dict))

    def test_from_db_object_to_cluster_object(self):
        """test conversion of database object to Cluster object."""
        cluster = self.get_test_cluster()
        cue_cluster = objects.Cluster()
        db_cluster = models.Cluster()
        db_cluster.update(cluster)

        objects.Cluster._from_db_object(cue_cluster, db_cluster)
        test_utils.validate_cluster_values(self, cluster, cue_cluster)

    def test_from_db_object_to_cluster_object_invalid_field(self):
        """test conversion of database object to Cluster object with an

        invalid field.
        """
        cluster = self.get_test_cluster()
        cluster['endpoint'] = '10.0.0.4:5672'
        db_cluster = models.Cluster()
        db_cluster.update(cluster)
        cue_cluster = objects.Cluster()

        objects.Cluster._from_db_object(cue_cluster, db_cluster)
        self.assertRaises(AttributeError, lambda: cue_cluster.endpoint)