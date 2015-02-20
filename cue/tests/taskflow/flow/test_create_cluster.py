# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import uuid

from cue import client
from cue.db.sqlalchemy import models
from cue import objects
from cue.taskflow.flow import create_cluster
from cue.tests import base
from cue.tests.test_fixtures import neutron
from cue.tests.test_fixtures import nova
from cue.tests.test_fixtures import telnet

from taskflow import engines
import taskflow.exceptions as taskflow_exc


class CreateClusterTests(base.TestCase):
    additional_fixtures = [
        nova.NovaClient,
        neutron.NeutronClient,
        telnet.TelnetClient
    ]

    def setUp(self):

        super(CreateClusterTests, self).setUp()

        flavor_name = "m1.tiny"

        self.nova_client = client.nova_client()
        self.neutron_client = client.neutron_client()

        self.new_vm_name = uuid.uuid4().hex
        self.new_vm_list = []

        image_list = self.nova_client.images.list()
        for image in image_list:
            if (image.name.startswith("cirros")) and (
                    image.name.endswith("kernel")):
                break
        self.valid_image = image

        self.valid_flavor = self.nova_client.flavors.find(name=flavor_name)

        network_list = self.neutron_client.list_networks()
        self.valid_network = network_list['networks'][0]

    def test_create_cluster(self):
        flow_store = {
            "image": self.valid_image.id,
            "flavor": self.valid_flavor.id,
            "network_id": self.valid_network['id'],
            "rabbit_port": '5672',
        }

        cluster_values = {
            "project_id": self.context.tenant_id,
            "name": "RabbitCluster",
            "network_id": uuid.uuid4(),
            "flavor": "1",
            "size": 3,
        }

        new_cluster = objects.Cluster(**cluster_values)
        new_cluster.create(self.context)

        nodes = objects.Node.get_nodes_by_cluster_id(self.context,
                                                     new_cluster.id)

        node_ids = []
        for node in nodes:
            node_ids.append(node.id)

        flow = create_cluster(self.context.to_dict(), new_cluster.id, node_ids)

        result = engines.run(flow, store=flow_store)
        nodes_after = objects.Node.get_nodes_by_cluster_id(self.context,
                                                           new_cluster.id)

        for i, node in enumerate(nodes_after):
            self.assertEqual(models.Status.ACTIVE, result["vm_status_%d" % i])
            self.new_vm_list.append(result["vm_id_%d" % i])
            self.assertEqual(models.Status.ACTIVE, node.status,
                             "Invalid status for node %d" % i)

    def test_create_cluster_overlimit(self):
        vm_list = self.nova_client.servers.list()
        port_list = self.neutron_client.list_ports()

        flow_store = {
            'image': self.valid_image.id,
            'flavor': self.valid_flavor.id,
            'network_id': self.valid_network['id']
        }

        cluster_id = uuid.uuid4().hex
        cluster_size = 10
        flow = create_cluster(cluster_id, cluster_size)

        self.assertRaises(taskflow_exc.WrappedFailure, engines.run,
                          flow, store=flow_store)

        self.assertEqual(vm_list, self.nova_client.servers.list())
        self.assertEqual(port_list, self.neutron_client.list_ports())

    def tearDown(self):
        for vm_id in self.new_vm_list:
            self.nova_client.servers.delete(vm_id)
        super(CreateClusterTests, self).tearDown()
