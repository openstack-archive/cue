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


from cue import client
from cue.tests.functional import base
from cue.tests.functional.fixtures import neutron
from cue.tests.functional.fixtures import nova
import os_tasklib.nova.list_vm_interfaces as list_vm_interfaces

import novaclient.exceptions as nova_exc
from oslo_utils import uuidutils
from taskflow import engines
from taskflow.patterns import linear_flow


class GetVmInterfacesTests(base.FunctionalTestCase):
    additional_fixtures = [
        neutron.NeutronClient,
        nova.NovaClient,
    ]

    def setUp(self):
        super(GetVmInterfacesTests, self).setUp()

        flavor_name = "m1.tiny"

        self.nova_client = client.nova_client()
        self.neutron_client = client.neutron_client()

        self.valid_vm_name = uuidutils.generate_uuid()

        image_list = self.nova_client.images.list()
        for image in image_list:
            if (image.name.startswith("cirros")) and (
                    image.name.endswith("kernel")):
                break
        valid_image = image

        valid_flavor = self.nova_client.flavors.find(name=flavor_name)

        network_name = "private"
        networks = self.neutron_client.list_networks(name=network_name)
        network = networks['networks'][0]
        self.valid_net_id = network['id']
        nics = [{'net-id': self.valid_net_id}]

        new_vm = self.nova_client.servers.create(name=self.valid_vm_name,
                                                 image=valid_image,
                                                 flavor=valid_flavor,
                                                 nics=nics)
        self.valid_vm_id = new_vm.id

        self.flow = linear_flow.Flow("create vm flow")
        self.flow.add(
            list_vm_interfaces.ListVmInterfaces(
                os_client=self.nova_client,
                requires=('server',),
                provides=('interface_list')
            )
        )

    def test_get_valid_vm_interfaces(self):
        flow_store = {
            'server': self.valid_vm_id
        }

        result = engines.run(self.flow, store=flow_store)
        interface_list = result['interface_list']
        self.assertEqual(self.valid_net_id, interface_list[0]['net_id'])

    def test_get_vm_interfaces_invalid_vm(self):
        flow_store = {
            'server': uuidutils.generate_uuid()
        }

        self.assertRaises(nova_exc.NotFound, engines.run, self.flow,
                          store=flow_store)

    def test_get_vm_interfaces_invalid_vm_ignore_not_found_exception(self):
        flow_store = {
            'server': uuidutils.generate_uuid(),
            'ignore_nova_not_found_exception': True
        }

        result = engines.run(self.flow, store=flow_store)
        interface_list = result['interface_list']
        self.assertEqual([], interface_list)

    def tearDown(self):
        if self.valid_vm_id is not None:
            self.nova_client.servers.delete(self.valid_vm_id)
        super(GetVmInterfacesTests, self).tearDown()
