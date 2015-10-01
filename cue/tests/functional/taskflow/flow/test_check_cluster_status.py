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
from cue.db import api as db_api
from cue.db.sqlalchemy import models
from cue import objects
from cue.taskflow.flow import check_cluster_status
from cue.taskflow.flow import create_cluster
from cue.tests.functional import base
from cue.tests.functional.fixtures import neutron
from cue.tests.functional.fixtures import nova
from cue.tests.functional.fixtures import urllib2_fixture

from taskflow import engines


class CheckClusterStatusTests(base.FunctionalTestCase):
    additional_fixtures = [
        nova.NovaClient,
        neutron.NeutronClient,
        urllib2_fixture.Urllib2Fixture
    ]
    dbapi = db_api.get_instance()

    def setUp(self):

        super(CheckClusterStatusTests, self).setUp()

        flavor_name = "m1.tiny"
        network_name = "private"
        management_network_name = "cue_management_net"

        self.nova_client = client.nova_client()
        self.neutron_client = client.neutron_client()
        self.port = '5672'

        self.new_vm_name = str(uuid.uuid4())
        self.new_vm_list = []

        image_list = self.nova_client.images.list()
        for image in image_list:
            if (image.name.startswith("cirros")) and (
                    image.name.endswith("kernel")):
                break
        self.valid_image = image

        self.valid_flavor = self.nova_client.flavors.find(name=flavor_name)

        network_list = self.neutron_client.list_networks(name=network_name)
        self.valid_network = network_list['networks'][0]

        network_list = self.neutron_client.list_networks(
            name=management_network_name)
        self.management_network = network_list['networks'][0]

        # Todo(Dan) If testing becomes asynchronous, then there is no guarantee
        # that these urllib return results will come in the proper order.  Will
        # have to update the urllib2 fixture to respond appropriately for the
        # url passed in.
        urllib2_fixture.Urllib2ResultDetails.set_urllib2_result(
            ['{"status": "ok"}',
             '[{"name": "/"}]'
             ]
        )

    def test_check_cluster_status(self):
        flow_store_create = {
            "image": self.valid_image.id,
            "flavor": self.valid_flavor.id,
            "port": self.port,
            "context": self.context.to_dict(),
            "erlang_cookie": str(uuid.uuid4()),
            "default_rabbit_user": 'rabbit',
            "default_rabbit_pass": str(uuid.uuid4()),
        }
        flow_store_check = {
            "context": self.context.to_dict(),
            "default_rabbit_user": "user",
            "default_rabbit_pass": "pass"
        }

        cluster_values = {
            "project_id": self.context.tenant_id,
            "name": "RabbitCluster",
            "network_id": str(uuid.uuid4()),
            "flavor": "1",
            "size": 2,
        }

        new_cluster = objects.Cluster(**cluster_values)
        new_cluster.create(self.context)

        nodes = objects.Node.get_nodes_by_cluster_id(self.context,
                                                     new_cluster.id)
        node_ids = []
        for node in nodes:
            node_ids.append(str(node.id))

        flow_create = create_cluster(new_cluster.id,
                              node_ids,
                              self.valid_network['id'],
                              self.management_network['id'])
        engines.run(flow_create, store=flow_store_create)

        cluster_before = objects.Cluster.get_cluster_by_id(self.context,
                                                          new_cluster.id)
        self.assertEqual(models.Status.ACTIVE, cluster_before.status,
                         "Invalid status for cluster")

        urllib2_fixture.Urllib2ResultDetails.set_urllib2_result(
            ['{"status": "not-ok"}',
             '[{"name": "/"}]',
             '{"status": "not-ok"}',
             '[{"name": "/"}]',
            ]
        )
        flow_check_status = check_cluster_status(str(new_cluster.id), node_ids)
        engines.run(flow_check_status, store=flow_store_check)

        cluster_after = objects.Cluster.get_cluster_by_id(self.context,
                                                          new_cluster.id)
        self.assertEqual(models.Status.ERROR, cluster_after.status,
                         "Invalid status for cluster")

    def tearDown(self):
        for vm_id in self.new_vm_list:
            self.nova_client.servers.delete(vm_id)
        super(CheckClusterStatusTests, self).tearDown()