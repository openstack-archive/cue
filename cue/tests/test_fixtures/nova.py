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

import novaclient.exceptions as nova_exc
import novaclient.v2.client as nova_client

import cue.client as client
import cue.tests.test_fixtures.base as base


class VmDetails(object):
    def __init__(self, vm_id, name, flavor, image, status=None):
        self.id = vm_id
        self.name = name
        self.flavor = flavor
        self.image = image
        self.status = status if status else 'ACTIVE'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'flavor': self.flavor,
            'image': self.image,
            'status': self.status
        }


class ImageDetails(object):
    def __init__(self, created=None, human_id=None, id=None, minDisk=None,
                 minRam=None, name=None, progress=None, status=None,
                 updated=None):
        self.created = created
        self.human_id = human_id
        self.id = id
        self.minDisk = minDisk
        self.minRam = minRam
        self.name = name
        self.progress = progress
        self.status = status or 'ACTIVE'
        self.updated = updated


class FlavorDetails(object):
    def __init__(self, disk=None, ephemeral=None, id=None, is_public=None,
                 name=None, ram=None, rxtx_factor=None, swap=None, vcpus=None):
        self.disk = disk or 10
        self.ephemeral = ephemeral or 10
        self.id = id or uuid.uuid4().hex
        self.is_public = is_public or 'N/A'
        self.name = name
        self.ram = ram or 512
        self.rxtx_factor = rxtx_factor or 1.0
        self.swap = swap or 0
        self.vcpus = vcpus or 2


class VmStatusDetails(object):
    vm_status_list = []

    @staticmethod
    def set_vm_status(statuses):
        """Helper function to setup sequence of status labels provided to a VM.

        :param statuses: list of statuses
        """
        for status in statuses:
            VmStatusDetails.vm_status_list.append(status)

    @staticmethod
    def get_status():
        """Returns the next status in configured sequence.

        If status sequence is empty, a status of 'ACTIVE' is returned.

        :return: Current VM status.
        """
        if len(VmStatusDetails.vm_status_list) == 0:
            status = 'ACTIVE'
        else:
            status = VmStatusDetails.vm_status_list.pop()

        return status


class NovaClient(base.BaseFixture):
    """A test fixture to simulate a Nova Client connection

    This class is used in test cases to simulate a real Nova Client
    connection in the absence of a working Neutron API endpoint.
    """

    def __init__(self, image_list=None, flavor_list=None,
                 vm_limit=None, *args, **kwargs):
        super(NovaClient, self).__init__(*args, **kwargs)
        self._vm_list = dict()
        self._image_list = dict()
        self._flavor_list = dict()

        if not image_list:
            image_list = ['cirros-0.3.2-x86_64-uec-kernel']

        if not flavor_list:
            flavor_list = ['m1.tiny']

        self._vm_limit = vm_limit if vm_limit else 3

        for image in image_list:
            image_detail = ImageDetails(name=image)
            self._image_list.update({
                image_detail.id: image_detail
            })

        for flavor in flavor_list:
            flavor_detail = FlavorDetails(name=flavor)
            self._flavor_list.update({
                flavor_detail.id: flavor_detail
            })

    def setUp(self):
        """Set up test fixture and apply all method overrides."""
        super(NovaClient, self).setUp()

        v2_client = self.mock(nova_client.Client)
        v2_client.servers.create = self.create_vm
        v2_client.servers.delete = self.delete_vm
        v2_client.servers.get = self.get_vm
        v2_client.servers.list = self.list_vms
        v2_client.images.find = self.images_find
        v2_client.images.list = self.list_images
        v2_client.flavors.find = self.flavors_find

    def create_vm(self, name, image, flavor, nics=None, **kwargs):
        """Mock'd version of novaclient...create_vm().

        Create a Nova VM.

        :param body: Dictionary with vm information.
        :return: An updated copy of the 'body' that was passed in, with other
                 information populated.
        """
        if len(self._vm_list) >= self._vm_limit:
            raise nova_exc.OverLimit(413)
        try:
            flavor_id = flavor.id
        except AttributeError:
            flavor_id = flavor

        try:
            image_id = image.id
        except AttributeError:
            image_id = image

        if not self._flavor_list.get(flavor_id):
            raise nova_exc.BadRequest(400)

        if not self._image_list.get(image_id):
            raise nova_exc.BadRequest(400)

        if nics is not None:
            neutron_client = client.neutron_client()
            for nic in nics:
                if nic.get('net-id'):
                    network_list = neutron_client.list_networks(
                        id=nic['net-id'])
                    if (not network_list or
                            not network_list.get('networks') or
                                len(network_list['networks']) == 0):
                        raise nova_exc.BadRequest(400)
                if nic.get('port-id'):
                    pass

        newVm = VmDetails(vm_id=uuid.uuid4(), name=name,
                          flavor=flavor, image=image,
                          status='BUILDING')

        self._vm_list[newVm.id] = newVm

        return newVm

    def delete_vm(self, server, **kwargs):
        """Mock'd version of novaclient...delete_vm().

        :param server: vm object with populated id instance variable
        :return: n/a
        """
        try:
            server_id = server.id
        except AttributeError:
            server_id = server

        try:
            del (self._vm_list[server_id])
        except KeyError:
            raise nova_exc.NotFound("Invalid server provided")

    def get_vm(self, server, **kwargs):
        """Mock'd version of novaclient...get()

        :param server: vm object with populated id instance variable
        :return: current server object for specified vm id
        """
        try:
            server_id = server.id
        except AttributeError:
            server_id = server

        try:
            server = self._vm_list[server_id]
        except KeyError:
            raise nova_exc.NotFound(404)

        server.status = VmStatusDetails.get_status()

        return server

    def list_vms(self, retrieve_all=True, **_params):
        """Mock'd version of novaclient...list_vms().

        List available vms.

        :param retrieve_all: Set to true to retrieve all available vms
        """
        if retrieve_all:
            return self._vm_list.values()

    def images_find(self, name, **kwargs):
        """Mock'd version of novaclient...image_find().

        Finds an image detail based on provided name

        :param name: Image name.
        :return: Image detail matching provided image name.
        """
        for image_detail in self._image_list.itervalues():
            if image_detail.name == name:
                return image_detail

    def list_images(self, retrieve_all=True, **_params):
        """Mock'd version of novaclient...list_images().

        List available images.

        :param retrieve_all: Set to true to retrieve all available images
        """
        if retrieve_all:
            return self._image_list.values()

    def flavors_find(self, name, **kwargs):
        """Mock'd version of novaclient...flavors_find().

        Finds a flavor detail based on provided name.

        :param name: Flavor name.
        :return: Flavor detail matching provided flavor name.
        """
        for flavor_detail in self._flavor_list.itervalues():
            if flavor_detail.name == name:
                return flavor_detail