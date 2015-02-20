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
from cue.tests.test_fixtures import nova
import os_tasklib.nova.get_vm as get_vm

import novaclient.exceptions as nova_exc
from taskflow import engines
from taskflow.patterns import linear_flow


class GetVmTests(base.TestCase):
    additional_fixtures = [
        nova.NovaClient,
    ]

    def setUp(self):
        super(GetVmTests, self).setUp()

        flavor_name = "m1.tiny"

        self.nova_client = client.nova_client()

        self.valid_vm_name = uuid.uuid4().hex

        image_list = self.nova_client.images.list()
        for image in image_list:
            if (image.name.startswith("cirros")) and (
                    image.name.endswith("kernel")):
                break
        valid_image = image

        valid_flavor = self.nova_client.flavors.find(name=flavor_name)
        new_vm = self.nova_client.servers.create(name=self.valid_vm_name,
                                                 image=valid_image,
                                                 flavor=valid_flavor)
        self.valid_vm_id = new_vm.id

        self.flow = linear_flow.Flow("create vm flow")
        self.flow.add(
            get_vm.GetVm(
                os_client=self.nova_client,
                requires=('server',),
                provides=('vm_info')
            )
        )

    def test_get_valid_vm(self):
        flow_store = {
            'server': self.valid_vm_id
        }

        result = engines.run(self.flow, store=flow_store)
        new_vm = result['vm_info']
        self.assertEqual(self.valid_vm_id, new_vm['id'])
        self.assertEqual(self.valid_vm_name, new_vm['name'])

    def test_get_invalid_vm(self):
        invalid_vm_id = uuid.uuid4().hex
        flow_store = {
            'server': invalid_vm_id
        }

        self.assertRaises(nova_exc.NotFound, engines.run,
                          self.flow, store=flow_store)

    def tearDown(self):
        if self.valid_vm_id is not None:
            self.nova_client.servers.delete(self.valid_vm_id)
        super(GetVmTests, self).tearDown()
