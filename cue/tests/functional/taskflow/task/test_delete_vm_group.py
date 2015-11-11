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
from cue.tests.functional import base
from cue.tests.functional.fixtures import nova
import os_tasklib.nova.delete_vm_group as delete_vm_group

import novaclient.exceptions as nova_exc
from taskflow import engines
from taskflow.patterns import linear_flow


class DeleteVmGroupTests(base.FunctionalTestCase):
    additional_fixtures = [
        nova.NovaClient
    ]

    task_store = {
        'group': "0",
    }

    def setUp(self):
        super(DeleteVmGroupTests, self).setUp()

        self.nova_client = client.nova_client()

        self.new_vm_group_name = str(uuid.uuid4())
        self.new_vm_group_id = None

        self.flow = linear_flow.Flow("delete vm group flow")
        self.flow.add(
            delete_vm_group.DeleteVmGroup(os_client=self.nova_client)
        )

    def test_delete_server_group_invalid_id(self):
        """Verifies Delete non-existing server group."""
        # create a few server groups
        server_groups = [
            self.nova_client.server_groups.create(name="server_group_1",
                                                  policies=['anti-affinity']),
            self.nova_client.server_groups.create(name="server_group_2",
                                                  policies=['affinity']),
            self.nova_client.server_groups.create(name="server_group_3",
                                                  policies=['anti-affinity'])]

        self.task_store['group'] = str(uuid.uuid4())

        # start engine to run delete task
        engines.run(self.flow, store=DeleteVmGroupTests.task_store)

        # retrieve all server groups
        server_groups_found = []
        for server_group in server_groups:
            server_groups_found.append(
                self.nova_client.server_groups.get(server_group.id))

        # verify the number of server groups did not change
        self.assertEqual(len(server_groups), len(server_groups_found),
                         "Not all server groups were found")

    def test_delete_server_group(self):
        """Verifies Delete existing server group."""
        # create a few server groups
        server_groups = [
            self.nova_client.server_groups.create(name="server_group_1",
                                                  policies=['anti-affinity']),
            self.nova_client.server_groups.create(name="server_group_2",
                                                  policies=['anti-affinity']),
            self.nova_client.server_groups.create(name="server_group_3",
                                                  policies=['affinity'])]

        # select a server group to delete
        self.task_store['group'] = server_groups[0].id

        # start engine to run delete server group task
        engines.run(self.flow, store=DeleteVmGroupTests.task_store)

        # verify deleted server group is not found
        self.assertRaises(nova_exc.NotFound,
                          self.nova_client.server_groups.get,
                          server_groups[0].id)
