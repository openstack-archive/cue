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


from neutronclient.common import exceptions
import neutronclient.neutron.client
from oslo_utils import uuidutils

import cue.tests.functional.fixtures.base as base


def new_network_detail(admin_state_up=True,
                       id=None,
                       name=None,
                       port_security_enabled=True,
                       router_external=False,
                       shared=False,
                       status='ACTIVE',
                       subnets=None,
                       tenant_id=None):
    if id is None:
        id = uuidutils.generate_uuid()
    if tenant_id is None:
        tenant_id = uuidutils.generate_uuid()
    return {'admin_state_up': admin_state_up,
            'id': id,
            'name': name,
            'port_security_enabled': port_security_enabled,
            'router:external': router_external,
            'shared': shared,
            'status': status,
            'subnets': subnets,
            'tenant_id': tenant_id}


class NeutronClient(base.BaseFixture):
    """A test fixture to simulate a Neutron Client connection

    This class is used in test cases to simulate a real Neutron Client
    connection in the absence of a working Neutron API endpoint.
    """

    def __init__(self, *args, **kwargs):
        super(NeutronClient, self).__init__(*args, **kwargs)

        self._network_list = {}
        self._port_list = {}

        initial_networks = ["private", "cue_management_net"]
        for network in initial_networks:
            network_detail = new_network_detail(name=network)
            self._network_list.update({network_detail['id']: network_detail})

    def setUp(self):
        """Set up test fixture and apply all method overrides."""
        super(NeutronClient, self).setUp()

        v2_client = self.mock(neutronclient.neutron.client.API_VERSIONS['2.0'])
        v2_client.create_port = self.create_port
        v2_client.create_network = self.create_network
        v2_client.list_ports = self.list_ports
        v2_client.list_networks = self.list_networks
        v2_client.delete_port = self.delete_port
        v2_client.show_network = self.show_network

    def create_port(self, body=None):
        """Mock'd version of neutronclient...create_port().

        Create a Neutron network port.

        :param body: Dictionary with port information.
        :return: An updated copy of the 'body' that was passed in, with other
                 information populated.
        """
        if body and body['port'] and body['port']['network_id']:
            network_id = body['port']['network_id']
            if network_id not in self._network_list:
                raise exceptions.NetworkNotFoundClient(
                    "network %s not found" % network_id
                )
        else:
            body = {'port': {}}

        port_id = uuidutils.generate_uuid()
        body['port']['id'] = port_id
        body['port']['fixed_ips'] = []
        body['port']['fixed_ips'].append({'ip_address': '0.0.0.0'})
        self._port_list[port_id] = body['port'].copy()
        return body

    def create_network(self, body=None):
        """Mock'd version of neutronclient...create_network().

        Create a Neutron network.

        :param body: Dictionary with network information.
        :return: An updated copy of the 'body' that was passed in, with other
                 information populated.
        """
        if body and body['network']:
            pass
        else:
            body = {'network': {}}

        network_id = uuidutils.generate_uuid()
        body['network'].update({
            'id': network_id,
            'subnets': [],
            'tenant_id': network_id,
            'segments': [],
            'shared': False,
            'port_security_enabled': True,
        })
        self._network_list[network_id] = body
        return body

    def list_ports(self, retrieve_all=True, **_params):
        """Mock'd version of neutronclient...list_ports().

        List available ports.

        :param retrieve_all: Set to true to retrieve all available ports
        """
        if retrieve_all:
            return {'ports': list(self._port_list.values())}

    def list_networks(self, name=None, id=None):
        if name is not None:
            property = 'name'
            value = name
        elif id is not None:
            property = 'id'
            value = id

        else:
            return {'networks': self._network_list.values()}

        for network in self._network_list.values():
            if network[property] == value:
                return {'networks': [network]}

    def delete_port(self, port):
        try:
            port_id = port.id
        except AttributeError:
            port_id = port

        if port_id in self._port_list:
            self._port_list.pop(port_id)
        else:
            raise exceptions.NeutronClientException("404 Not found")

    def show_network(self, network):
        try:
            network_id = network.id
        except AttributeError:
            network_id = network

        if network_id in self._network_list:
            return {'network': self._network_list[network_id]}
        else:
            raise exceptions.NeutronClientException(
                "Network " + network_id + " could not be found.")
