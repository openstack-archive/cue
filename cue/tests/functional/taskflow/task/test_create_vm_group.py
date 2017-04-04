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
from cue.tests.functional.fixtures import nova
import os_tasklib.nova.create_vm_group as create_vm_group

from oslo_utils import uuidutils
from taskflow import engines
from taskflow.patterns import linear_flow


class CreateVmGroupTests(base.FunctionalTestCase):
    additional_fixtures = [
        nova.NovaClient
    ]

    def setUp(self):
        super(CreateVmGroupTests, self).setUp()

        self.nova_client = client.nova_client()

        self.new_vm_group_name = uuidutils.generate_uuid()
        self.new_vm_group_id = None

        self.flow = linear_flow.Flow("create vm group flow")
        self.flow.add(
            create_vm_group.CreateVmGroup(
                os_client=self.nova_client,
                requires=('name', 'policies'),
                provides='new_vm_group',
                rebind={'name': 'vm_group_name'}
            )
        )

    def test_create_vm_group(self):
        """Verifies CreateVMGroup task directly."""

        flow_store = {
            'vm_group_name': self.new_vm_group_name,
            'policies': ['anti-affinity']
        }

        result = engines.run(self.flow, store=flow_store)
        self.new_vm_group_id = result['new_vm_group']['id']
        vm_group = self.nova_client.server_groups.get(self.new_vm_group_id)
        self.assertEqual(self.new_vm_group_name, vm_group.name)
