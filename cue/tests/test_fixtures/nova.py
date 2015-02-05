# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import uuid

import novaclient.v1_1.client as nova_client

import cue.tests.test_fixtures.base as base


class VmDetails():
    def __init__(self, vm_id, name, flavor):
        self.id = vm_id
        self.name = name
        self.flavor = flavor


class NovaClient(base.BaseFixture):
    """A test fixture to simulate a Nova Client connection

    This class is used in test cases to simulate a real Nova Client
    connection in the absence of a working Neutron API endpoint.
    """

    def setUp(self):
        """Set up test fixture and apply all method overrides."""
        super(NovaClient, self).setUp()

        self._vm_list = {}

        v2_client = self.mock(nova_client.Client)
        v2_client.servers.create = self.create_vm
        v2_client.servers.delete = self.delete_vm
        v2_client.servers.list = self.list_vms

    def create_vm(self, **params):
        """Mock'd version of novaclient...create_vm().

        Create a Nova VM.

        :param body: Dictionary with vm information.
        :return: An updated copy of the 'body' that was passed in, with other
                 information populated.
        """
        newVm = VmDetails(vm_id=uuid.uuid4(), name=params['name'],
                          flavor=params['flavor'])

        self._vm_list[newVm.id] = newVm

        return newVm

    def delete_vm(self, vm):
        """Mock'd version of novaclient...delete_vm().

        :param vm object with id instance variable
        :return: n/a
        """
        del(self._vm_list[vm.id])

    def list_vms(self, retrieve_all=True, **_params):
        """Mock'd version of novaclient...list_vms().

        List available vms.

        :param retrieve_all: Set to true to retrieve all available ports
        """
        if retrieve_all:
            return self._vm_list.values()