#    Copyright 2014 Rackspace
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
# Copied from Octavia
import uuid

from cue.common import exception
from cue.db.sqlalchemy import api
from cue.db.sqlalchemy import models
from cue.tests import base


UUID1 = str(uuid.uuid4())
UUID2 = str(uuid.uuid4())


class ClusterTests(base.TestCase):
    def test_create(self):
        """Verifies a new cluster record is created in DB."""

        data = {
            "project_id": UUID1,
            "name": "test",
            "status": models.Status.BUILDING,
            "nic": UUID2,
            "volume_size": 0,
            "deleted": False
        }
        ref = models.Cluster.create(self.session, **data)
        self.assertIsInstance(ref, models.Cluster)

        self.session = api.get_session()
        get_ref = models.Cluster.get(self.session, id=ref.id)
        self.assertEqual(ref.id, get_ref.id, "Database object does not match "
                                             "submitted object")

    def test_update(self):
        """Verifies update record function."""

        data = {
            "project_id": UUID1,
            "name": "test",
            "status": models.Status.BUILDING,
            "nic": UUID2,
            "volume_size": 0,
            "deleted": False
        }
        ref = models.Cluster.create(self.session, **data)
        self.assertIsInstance(ref, models.Cluster)

        self.session = api.get_session()
        data2 = {
            "name": "NewName",
            "status": "ACTIVE"
        }
        models.Cluster.update(self.session, ref.id, **data2)

        self.session = api.get_session()
        get_ref = models.Cluster.get(self.session, id=ref.id)
        self.assertEqual(str(ref.name), 'test', "Original cluster name was"
                                                "unexpectedly changed")
        self.assertEqual(str(get_ref.name), 'NewName', "Cluster name was not "
                                                       "updated")
        self.assertEqual(str(get_ref.status), 'ACTIVE', "Cluster status was "
                                                        "not updated")
        self.assertGreater(get_ref.updated_at, ref.updated_at, "Updated "
                                                               "datetime was "
                                                               "not updated.")

    def test_delete(self):
        """Verifies deleting existing record is removed from DB."""

        data = {
            "project_id": UUID1,
            "name": "test",
            "nic": UUID2,
            "volume_size": 0,
            "status": models.Status.BUILDING,
            "deleted": False
        }
        ref = models.Cluster.create(self.session, **data)
        self.assertIsInstance(ref, models.Cluster)

        models.Cluster.delete(self.session, ref.id)

        self.session = api.get_session()

        try:
            get_ref = models.Cluster.get(self.session, id=ref.id)
        except exception.NotFound:
            self.fail('Record was deleted entirely')
        else:
            if get_ref.status != models.Status.DELETING:
                self.fail('Record status was not update to DELETING')

    def test_get_delete_batch(self):
        """Verifies delete batch records from DB."""

        data = {
            "project_id": UUID1,
            "name": "test1",
            "status": models.Status.BUILDING,
            "nic": UUID2,
            "volume_size": 0,
            "deleted": False
        }
        ref1 = models.Cluster.create(self.session, **data)
        self.assertIsInstance(ref1, models.Cluster)
        data.update(name="test2")
        ref2 = models.Cluster.create(self.session, **data)
        self.assertIsInstance(ref2, models.Cluster)
        data.update(name="test3")
        ref3 = models.Cluster.create(self.session, **data)
        self.assertIsInstance(ref3, models.Cluster)
        data.update(name="test4")
        ref4 = models.Cluster.create(self.session, **data)
        self.assertIsInstance(ref4, models.Cluster)

        self.session = api.get_session()

        clusters_before = models.Cluster.get_all(self.session,
                                                 status=models.Status.BUILDING)

        ids = [ref1.id, ref2.id, ref3.id, ref4.id]
        self.assertEqual(len(ids), len(clusters_before), "Not able to get "
                                                         "all created "
                                                         "clusters")

        models.Cluster.delete_batch(self.session, ids)
        clusters_after = models.Cluster.get_all(self.session,
                                                status=models.Status.DELETING)

        self.assertEqual(len(ids), len(clusters_after), "Not all cluster "
                                                        "record's statuses "
                                                        "were marked as "
                                                        "deleted")


class NodeRepositoryTests(base.TestCase):
    def test_create(self):
        """Verifies a new cluster record and a new node record pointed to

        correct cluster are created.
        """

        cluster = {
            "project_id": UUID1,
            "name": "test",
            "nic": UUID2,
            "volume_size": 0,
            "status": "BUILDING",
            "deleted": False
        }

        cluster_ref = models.Cluster.create(self.session, **cluster)

        node = {
            "flavor": 'foo',
            "instance_id": 'bar',
            "cluster_id": cluster_ref.id,
            "volume_size": 0,
            "status": "BUILDING",
            "deleted": False
        }

        node_ref = models.Node.create(self.session, **node)
        self.assertIsInstance(node_ref, models.Node)
