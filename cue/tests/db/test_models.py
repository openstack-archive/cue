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

from cue.db import models
from cue.tests.db import base

UUID1 = str(uuid.uuid4())
UUID2 = str(uuid.uuid4())


class ClusterTests(base.TestCase):
    def test_create(self):
        data = {
            "project_id": UUID1,
            "name": "test",
            "nic": UUID2
        }
        ref = models.Cluster.create(self.session, **data)
        self.assertIsInstance(ref, models.Cluster)


class NodeRepositoryTests(base.TestCase):
    def test_create(self):
        cluster = {
            "project_id": UUID1,
            "name": "test",
            "nic": UUID2
        }

        cluster_ref = models.Cluster.create(self.session, **cluster)

        node = {
            "flavor": 'foo',
            "instance_id": 'bar',
            "cluster_id": cluster_ref.id
        }

        node_ref = models.Node.create(self.session, **node)
        self.assertIsInstance(node_ref, models.Node)
