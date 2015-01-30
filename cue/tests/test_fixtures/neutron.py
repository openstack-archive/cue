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

from neutronclient.common import exceptions
import neutronclient.neutron.client

import cue.tests.test_fixtures.base as base


class NeutronClient(base.BaseFixture):
    """A test fixture to simulate a Neutron Client connection

    This class is used in test cases to simulate a real Neutron Client
    connection in the absence of a working Neutron API endpoint.
    """

    def setUp(self):
        """Set up test fixture and apply all method overrides."""
        super(NeutronClient, self).setUp()

        self._network_list = {}
        self._port_list = {}

        v2_client = self.mock(neutronclient.neutron.client.API_VERSIONS['2.0'])
        v2_client.create_port = self.create_port
        v2_client.create_network = self.create_network
        v2_client.list_ports = self.list_ports

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

        port_id = uuid.uuid4()
        body['port']['id'] = port_id
        self._port_list[port_id] = body['port']
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

        network_id = uuid.uuid4()
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
            return {'ports': self._port_list.values()}