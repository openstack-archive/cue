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
import os_tasklib.nova.create_vm as create_vm

import novaclient.exceptions as nova_exc
from taskflow import engines
import taskflow.exceptions as taskflow_exc
from taskflow.patterns import linear_flow


class CreateVmTests(base.TestCase):
    additional_fixtures = [
        nova.NovaClient,
        neutron.NeutronClient
    ]

    def setUp(self):
        super(CreateVmTests, self).setUp()

        image_name = "cirros-0.3.2-x86_64-uec-kernel"
        flavor_name = "m1.tiny"
        network_name = "test-network"

        self.nova_client = client.nova_client()
        self.neutron_client = client.neutron_client()

        self.new_vm_name = uuid.uuid4().hex
        self.new_vm_id = None
        self.valid_image = self.nova_client.images.find(name=image_name)
        self.valid_flavor = self.nova_client.flavors.find(name=flavor_name)

        network_list = self.neutron_client.list_networks(name=network_name)
        self.valid_network = network_list['networks'][0]

        self.flow = linear_flow.Flow("create vm flow")
        self.flow.add(
            create_vm.CreateVm(
                os_client=self.nova_client,
                requires=('name', 'image', 'flavor', 'nics'),
                provides='new_vm',
                rebind={'name': 'vm_name'}
            )
        )

    def test_create_vm(self):
        flow_store = {
            'vm_name': self.new_vm_name,
            'image': self.valid_image.id,
            'flavor': self.valid_flavor.id,
            'nics': [{
                'net-id': self.valid_network['id']
            }]
        }

        result = engines.run(self.flow, store=flow_store)
        self.new_vm_id = result['new_vm']['id']
        new_vm = self.nova_client.servers.get(self.new_vm_id)
        self.assertEqual(self.new_vm_name, new_vm.name)

    def test_create_vm_invalid_flavor(self):
        invalid_flavor = uuid.uuid4().hex
        flow_store = {
            'vm_name': self.new_vm_name,
            'image': self.valid_image,
            'flavor': invalid_flavor,
            'nics': [{
                         'net-id': self.valid_network['id']
                     }]
        }

        self.assertRaises(nova_exc.BadRequest, engines.run,
                          self.flow, store=flow_store)

    def test_create_vm_invalid_image(self):
        invalid_image = uuid.uuid4().hex
        flow_store = {
            'vm_name': self.new_vm_name,
            'image': invalid_image,
            'flavor': self.valid_flavor,
            'nics': [{
                         'net-id': self.valid_network['id']
                     }]
        }

        self.assertRaises(nova_exc.BadRequest, engines.run,
                          self.flow, store=flow_store)

    def test_create_vm_invalid_nic(self):
        invalid_nic = uuid.uuid4().hex
        flow_store = {
            'vm_name': self.new_vm_name,
            'image': self.valid_image,
            'flavor': self.valid_flavor,
            'nics': [{
                         'net-id': invalid_nic
                     }]
        }

        self.assertRaises(nova_exc.BadRequest, engines.run,
                          self.flow, store=flow_store)

    def test_create_vm_missing_attributes(self):
        flow_store = {
        }

        self.assertRaises(taskflow_exc.MissingDependencies,
                          engines.run, self.flow, store=flow_store)

    def test_invalid_security_group(self):
        invalid_security_group = uuid.uuid4().hex
        flow_store = {
            'vm_name': self.new_vm_name,
            'image': self.valid_image.id,
            'flavor': self.valid_flavor.id,
            'security_groups': [invalid_security_group],
            'nics': [{
                         'net-id': self.valid_network['id']
                     }],
        }
        self.assertRaises(nova_exc.BadRequest, engines.run,
                          self.flow, store=flow_store)

    def tearDown(self):
        if self.new_vm_id is not None:
            self.nova_client.servers.delete(self.new_vm_id)
        super(CreateVmTests, self).tearDown()
