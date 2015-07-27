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
from cue.common import exception
from cue.db.sqlalchemy import models
from cue import objects
from cue.taskflow.flow import create_cluster
from cue.taskflow.flow import delete_cluster
from cue.tests.functional import base
from cue.tests.functional.fixtures import neutron
from cue.tests.functional.fixtures import nova
from cue.tests.functional.fixtures import urllib2

from taskflow import engines
import taskflow.exceptions as taskflow_exc


class DeleteClusterTests(base.FunctionalTestCase):
    additional_fixtures = [
        nova.NovaClient,
        neutron.NeutronClient,
        urllib2.Urllib2Fixture
    ]

    def setUp(self):

        super(DeleteClusterTests, self).setUp()

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
        urllib2.Urllib2ResultDetails.set_urllib2_result(
            ['{"status": "ok"}',
             '[{"name": "/"}]',
             '{"status": "ok"}',
             '[{"name": "/"}]',
             '{"status": "ok"}',
             '[{"name": "/"}]']
        )

    def test_delete_cluster(self):
        flow_store_create = {
            "image": self.valid_image.id,
            "flavor": self.valid_flavor.id,
            "port": self.port,
            "context": self.context.to_dict(),
            "erlang_cookie": str(uuid.uuid4()),
            "default_rabbit_user": 'rabbit',
            "default_rabbit_pass": str(uuid.uuid4()),
        }
        flow_store_delete = {
            "context": self.context.to_dict(),
        }

        cluster_values = {
            "project_id": self.context.tenant_id,
            "name": "RabbitCluster",
            "network_id": str(uuid.uuid4()),
            "flavor": "1",
            "size": 3,
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
        flow_delete = delete_cluster(str(new_cluster.id), node_ids)

        result = engines.run(flow_create, store=flow_store_create)

        nodes_after = objects.Node.get_nodes_by_cluster_id(self.context,
                                                           new_cluster.id)

        cluster_after = objects.Cluster.get_cluster_by_id(self.context,
                                                          new_cluster.id)

        self.assertEqual(models.Status.ACTIVE, cluster_after.status,
                         "Invalid status for cluster")

        for i, node in enumerate(nodes_after):
            self.assertEqual(models.Status.ACTIVE, result["vm_status_%d" % i])
            self.new_vm_list.append(result["vm_id_%d" % i])
            self.assertEqual(models.Status.ACTIVE, node.status,
                             "Invalid status for node %d" % i)
            endpoints = objects.Endpoint.get_endpoints_by_node_id(self.context,
                                                                  node.id)
            self.assertEqual(1, len(endpoints), "invalid number of endpoints "
                                                "received")
            endpoint = endpoints.pop()
            self.assertEqual(node.id, endpoint.node_id, "invalid endpoint node"
                                                        " id reference")

            uri = result['vm_user_ip_' + str(i)]
            uri += ':' + self.port
            self.assertEqual(uri, endpoint.uri, "invalid endpoint uri")
            self.assertEqual('AMQP', endpoint.type, "invalid endpoint type")

        result = engines.run(flow_delete, store=flow_store_delete)

        nodes_after = objects.Node.get_nodes_by_cluster_id(self.context,
                                                           new_cluster.id)

        self.assertRaises(exception.NotFound,
                          objects.Cluster.get_cluster_by_id,
                          self.context,
                          new_cluster.id)

        for i, node in enumerate(nodes_after):
            self.new_vm_list.remove(result["vm_id_%d" % i])
            self.assertEqual(models.Status.DELETED, node.status,
                             "Invalid status for node %d" % i)
            endpoints = objects.Endpoint.get_endpoints_by_node_id(self.context,
                                                                  node.id)
            self.assertEqual(0, len(endpoints), "endpoints were not deleted")

    def test_delete_invalid_cluster(self):
        vm_list = self.nova_client.servers.list()
        port_list = self.neutron_client.list_ports()

        flow_store_delete = {
            "context": self.context.to_dict(),
        }

        cluster_size = 3
        cluster_id = str(uuid.uuid4())
        node_ids = []
        for i in range(0, cluster_size):
            node_ids.append(str(uuid.uuid4()))

        flow_delete = delete_cluster(cluster_id, node_ids)

        self.assertRaises(taskflow_exc.WrappedFailure, engines.run,
                          flow_delete, store=flow_store_delete)

        self.assertEqual(vm_list, self.nova_client.servers.list())
        self.assertEqual(port_list, self.neutron_client.list_ports())

    def tearDown(self):
        for vm_id in self.new_vm_list:
            self.nova_client.servers.delete(vm_id)
        super(DeleteClusterTests, self).tearDown()