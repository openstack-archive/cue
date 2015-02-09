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

from cue.tests import base
from cue.tests.test_fixtures import nova
import os_tasklib.nova.delete_vm as delete_vm

from taskflow import engines
from taskflow.patterns import linear_flow


class DeleteVmTests(base.TestCase):
    additional_fixtures = [
        nova.NovaClient
    ]

    task_store = {
        'server': "0",
    }

    def setUp(self):
        super(DeleteVmTests, self).setUp()

        # create flow with "DeleteVm" task
        self.flow = linear_flow.Flow('create port').add(delete_vm.DeleteVm(
            os_client=self.clients["nova"]))

        image_list = self.clients["nova"].images.list()
        for image in image_list:
            if (image.name.startswith("cirros")) and (
                    image.name.endswith("kernel")):
                break
        self.valid_image = image

        self.flavor = self.clients["nova"].flavors.find(name="m1.tiny")

    def test_delete_vm_invalid_id(self):
        # create a few vms
        new_instances = [self.clients["nova"].servers.create(name="vm1",
                                                    image=self.valid_image,
                                                    flavor=self.flavor),
                         self.clients["nova"].servers.create(name="vm2",
                                                    image=self.valid_image,
                                                    flavor=self.flavor),
                         self.clients["nova"].servers.create(name="vm3",
                                                    image=self.valid_image,
                                                    flavor=self.flavor)]

        # delete non-existing vm (invalid id)
        DeleteVmTests.task_store['server'] = str(uuid.uuid4())

        # start engine to run delete task
        engines.run(self.flow, store=DeleteVmTests.task_store)

        # verify our existing vms have not been deleted
        vms = self.clients["nova"].servers.list()
        found = 0
        for vm in vms:
            for created_vm in new_instances:
                if vm.id == created_vm.id:
                    found += 1

        # cleanup
        for vm in new_instances:
            self.clients["nova"].servers.delete(vm)

        self.assertEqual(len(new_instances), found, "Not all VMs were found")

    def test_delete_vm(self):
        # create a few vms
        new_instances = [self.clients["nova"].servers.create(name="vm1",
                                                    image=self.valid_image,
                                                    flavor=self.flavor),
                         self.clients["nova"].servers.create(name="vm2",
                                                    image=self.valid_image,
                                                    flavor=self.flavor),
                         self.clients["nova"].servers.create(name="vm3",
                                                    image=self.valid_image,
                                                    flavor=self.flavor)]

        # delete one vm
        vm_to_delete = new_instances.pop()
        DeleteVmTests.task_store['server'] = str(vm_to_delete.id)

        # start engine to run delete task
        engines.run(self.flow, store=DeleteVmTests.task_store)

        # verify vm has been deleted
        vms = self.clients["nova"].servers.list()
        vm_found = False
        for vm in vms:
            if vm.id == vm_to_delete.id:
                vm_found = True
                break

        # cleanup
        for vm in new_instances:
            self.clients["nova"].servers.delete(vm)

        self.assertEqual(False, vm_found, "VM was not deleted successfully")