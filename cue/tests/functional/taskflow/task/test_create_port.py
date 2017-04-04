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


from cue import client
from cue.tests.functional import base
import cue.tests.functional.fixtures.neutron
import os_tasklib.neutron as neutron_task

from neutronclient.common import exceptions
from oslo_utils import uuidutils
from taskflow import engines
from taskflow.patterns import linear_flow

SHARED_CONF = {
    'connection': 'zookeeper',
}


class CreatePortTests(base.FunctionalTestCase):

    additional_fixtures = [
        cue.tests.functional.fixtures.neutron.NeutronClient
    ]

    task_store = {
        "network_id": "0",
        "port_name": "port_0",
    }

    def test_create_port_invalid_network(self):
        # retrieve neutron client API class
        neutron_client = client.neutron_client()

        # create flow with "CreatePort" task
        flow = linear_flow.Flow('create port').add(neutron_task.CreatePort(
            os_client=neutron_client, provides='neutron_port_id'))

        # generate a new UUID for an 'invalid' network_id
        CreatePortTests.task_store['network_id'] = uuidutils.generate_uuid()

        self.assertRaises(exceptions.NetworkNotFoundClient, engines.run, flow,
                          store=CreatePortTests.task_store)

    def test_create_port(self):
        # retrieve neutron client API class
        neutron_client = client.neutron_client()

        # set an existing network_id and unique name to use
        network_name = "private"
        networks = neutron_client.list_networks(name=network_name)
        network = networks['networks'][0]
        CreatePortTests.task_store['network_id'] = network['id']
        CreatePortTests.task_store['port_name'] = "port_" + (
        uuidutils.generate_uuid())

        # create flow with "CreatePort" task, given neutron client
        flow = linear_flow.Flow('create port').add(neutron_task.CreatePort(
            os_client=neutron_client, provides='neutron_port_id'))

        # execute flow with parameters required for "CreatePort" task
        engines.run(flow, store=CreatePortTests.task_store)

        # retrieve list of ports from Neutron service
        port_list = neutron_client.list_ports()

        # find our newly created port
        found = False
        for port in port_list['ports']:
            if port['network_id'] == CreatePortTests.task_store['network_id']:
                if port['name'] == CreatePortTests.task_store['port_name']:
                    found = True
                    break

        self.assertTrue(found, "New port was not found")
