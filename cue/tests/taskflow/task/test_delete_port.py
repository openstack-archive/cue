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

from cue import client
from cue.tests import base
import cue.tests.test_fixtures.neutron
import os_tasklib.neutron as neutron_task

import neutronclient.common.exceptions as neutron_exc
from taskflow import engines
from taskflow.patterns import linear_flow

SHARED_CONF = {
    'connection': 'zookeeper',
}


def _find_port(port_id, port_list):
    found = False
    for port in port_list['ports']:
        if port['id'] == port_id:
            found = True
            break

    return found


class DeletePortTests(base.TestCase):

    additional_fixtures = [
        cue.tests.test_fixtures.neutron.NeutronClient
    ]

    def setUp(self):
        super(DeletePortTests, self).setUp()

        network_name = 'test-network'

        self.neutron_client = client.neutron_client()

        network_list = self.neutron_client.list_networks(name=network_name)
        self.valid_network = network_list['networks'][0]

        # Delete port using DeletePort task
        self.flow = linear_flow.Flow('create port').add(
            neutron_task.DeletePort(os_client=self.neutron_client))

    def test_delete_existing_port(self):
        # create port
        body_value = {
            "port": {
                "admin_state_up": True,
                "name": "test port",
                "network_id": self.valid_network['id'],
                }
        }
        port_info = self.neutron_client.create_port(body=body_value)
        port_id = port_info['port']['id']

        # populate task_store with port-id of port created for this test
        task_store = {
            'port_id': port_id
        }

        # retrieve port list prior to delete
        pre_port_list = self.neutron_client.list_ports()

        # search for created port in port list
        self.assertEqual(True, _find_port(port_id, pre_port_list),
                         "port-id %s not found in neutron port list" % port_id)

        engines.run(self.flow, store=task_store)

        # retrieve port list after delete
        post_port_list = self.neutron_client.list_ports()

        # search for deleted port in port list
        self.assertEqual(False, _find_port(port_id, post_port_list),
                         "port-id %s found in neutron port after "
                         "delete" % port_id)

    def test_delete_nonexistent_port(self):
        # generate random port_id
        port_id = uuid.uuid4().hex

        task_store = {
            'port_id': port_id
        }

        # retrieve current port list
        pre_port_list = self.neutron_client.list_ports()
        self.assertEqual(False, _find_port(port_id, pre_port_list),
                         "port-id %s found in neutron port list" % port_id)

        # execute flow with parameters required for "CreatePort" task
        self.assertRaises(neutron_exc.NeutronClientException, engines.run,
                          self.flow, store=task_store)
