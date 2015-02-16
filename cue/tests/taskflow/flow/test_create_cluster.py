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
from cue.tests import base
from cue.tests.test_fixtures import neutron
from cue.tests.test_fixtures import nova
from cue.taskflow.flow import create_cluster

from taskflow import engines
import taskflow.exceptions as taskflow_exc


class CreateClusterTests(base.TestCase):
    additional_fixtures = [
        #nova.NovaClient,
        #neutron.NeutronClient
    ]

    def setUp(self):
        super(CreateClusterTests, self).setUp()

        if len(CreateClusterTests.additional_fixtures) > 0:
            image_name = "cirros-0.3.2-x86_64-uec-kernel"
            flavor_name = "m1.tiny"
            network_name = "test-network"
        else:
            image_name = "Ubuntu Server 14.04.1 LTS (amd64 20140927) - Partner Image"
            flavor_name = "standard.small"
            network_name = "min.pae@hp.com-network"

        self.nova_client = client.nova_client()
        self.neutron_client = client.neutron_client()

        self.new_vm_name = uuid.uuid4().hex
        self.new_vm_list = []
        self.valid_image = self.nova_client.images.find(name=image_name)
        self.valid_flavor = self.nova_client.flavors.find(name=flavor_name)

        network_list = self.neutron_client.list_networks(name=network_name)
        self.valid_network = network_list['networks'][0]

    def test_create_cluster(self):
        flow_store = {
            'image': self.valid_image.id,
            'flavor': self.valid_flavor.id,
            'network_id': self.valid_network['id']
        }

        cluster_id = uuid.uuid4().hex
        cluster_size = 3
        flow = create_cluster(cluster_id, cluster_size)

        result = engines.run(flow, store=flow_store)
        for i in range(cluster_size):
            self.assertEqual("ACTIVE", result["vm_status_%d" % i])
            self.new_vm_list.append(result["vm_id_%d" %i])

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
