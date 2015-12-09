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

from neutronclient.common import exceptions as neutron_exceptions
from oslo_config import cfg
from taskflow import engines
import taskflow.exceptions as taskflow_exc

from cue import client
from cue.common import exception as cue_exceptions
from cue.db.sqlalchemy import models
from cue import objects
from cue.taskflow.flow import create_cluster
from cue.tests.functional import base
from cue.tests.functional.fixtures import neutron
from cue.tests.functional.fixtures import nova
from cue.tests.functional.fixtures import urllib2_fixture


CONF = cfg.CONF


class CreateClusterTests(base.FunctionalTestCase):
    additional_fixtures = [
        nova.NovaClient,
        neutron.NeutronClient,
        urllib2_fixture.Urllib2Fixture
    ]

    def setUp(self):

        super(CreateClusterTests, self).setUp()

        flavor_name = "m1.tiny"
        network_name = "private"
        management_network_name = "cue_management_net"

        self.nova_client = client.nova_client()
        self.neutron_client = client.neutron_client()
        self.port = u'5672'

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
             '[{"name": "/"}]',
             '{"status": "ok"}',
             '[{"name": "/"}]',
             '{"status": "ok"}',
             '[{"name": "/"}]']
        )

    def test_create_cluster(self):
        flow_store = {
            "tenant_id": str(self.valid_network['tenant_id']),
            "image": self.valid_image.id,
            "flavor": self.valid_flavor.id,
            "port": self.port,
            "context": self.context.to_dict(),
            "erlang_cookie": str(uuid.uuid4()),
            "default_rabbit_user": 'rabbit',
            "default_rabbit_pass": str(uuid.uuid4()),
        }

        cluster_values = {
            "project_id": self.context.tenant_id,
            "name": "RabbitCluster",
            "network_id": self.valid_network['id'],
            "flavor": "1",
            "size": 3,
        }

        new_cluster = objects.Cluster(**cluster_values)
        new_cluster.create(self.context)

        nodes = objects.Node.get_nodes_by_cluster_id(self.context,
                                                     new_cluster.id)

        node_ids = []
        for node in nodes:
            node_ids.append(node.id)

        flow = create_cluster(new_cluster.id,
                              node_ids,
                              self.valid_network['id'],
                              self.management_network['id'])

        result = engines.run(flow, store=flow_store)

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

            node_ref = objects.Node.get_node_by_id(self.context, node.id)
            expected_management_ip = node_ref.management_ip
            actual_management_ip = result['vm_management_ip_' + str(i)]
            self.assertEqual(expected_management_ip, actual_management_ip,
                             "invalid management ip")

    def test_create_cluster_nova_error(self):
        flow_store = {
            "tenant_id": str(self.valid_network['tenant_id']),
            "image": self.valid_image.id,
            "flavor": self.valid_flavor.id,
            "port": self.port,
            "context": self.context.to_dict(),
            "erlang_cookie": str(uuid.uuid4()),
            "default_rabbit_user": 'rabbit',
            "default_rabbit_pass": str(uuid.uuid4()),
        }

        cluster_values = {
            "project_id": self.context.tenant_id,
            "name": "RabbitCluster",
            "network_id": self.valid_network['id'],
            "flavor": "1",
            "size": 3,
        }

        new_cluster = objects.Cluster(**cluster_values)
        new_cluster.create(self.context)

        nodes = objects.Node.get_nodes_by_cluster_id(self.context,
                                                     new_cluster.id)

        # configure custom vm_status list
        nova.VmStatusDetails.set_vm_status(['ACTIVE',
                                            'ERROR',
                                            'BUILD',
                                            'BUILD'])

        node_ids = []
        for node in nodes:
            node_ids.append(node.id)

        flow = create_cluster(new_cluster.id,
                              node_ids,
                              self.valid_network['id'],
                              self.management_network['id'])

        try:
            engines.run(flow, store=flow_store)
        except taskflow_exc.WrappedFailure as err:
            self.assertEqual(3, len(err._causes))
            exc_list = [type(c.exception) for c in err._causes]
            self.assertEqual([cue_exceptions.VmErrorException,
                              cue_exceptions.VmBuildingException,
                              cue_exceptions.VmBuildingException],
                             exc_list)
        except Exception as e:
            self.assertEqual(taskflow_exc.WrappedFailure, e)
        else:
            self.fail("Expected taskflow_exc.WrappedFailure exception.")

    def test_create_cluster_max_retries(self):
        flow_store = {
            "tenant_id": str(self.valid_network['tenant_id']),
            "image": self.valid_image.id,
            "flavor": self.valid_flavor.id,
            "port": self.port,
            "context": self.context.to_dict(),
            "erlang_cookie": str(uuid.uuid4()),
            "default_rabbit_user": 'rabbit',
            "default_rabbit_pass": str(uuid.uuid4()),
        }

        cluster_values = {
            "project_id": self.context.tenant_id,
            "name": "RabbitCluster",
            "network_id": self.valid_network['id'],
            "flavor": "1",
            "size": 1,
        }

        new_cluster = objects.Cluster(**cluster_values)
        new_cluster.create(self.context)

        nodes = objects.Node.get_nodes_by_cluster_id(self.context,
                                                     new_cluster.id)

        CONF.flow_options.create_cluster_node_vm_active_retry_count = 2

        # configure custom vm_status list
        nova.VmStatusDetails.set_vm_status(['BUILD',
                                            'BUILD',
                                            'BUILD'])

        node_ids = []
        for node in nodes:
            node_ids.append(node.id)

        flow = create_cluster(new_cluster.id,
                              node_ids,
                              self.valid_network['id'],
                              self.management_network['id'])

        self.assertRaises(cue_exceptions.VmBuildingException, engines.run,
                          flow, store=flow_store)

    def test_create_cluster_overlimit(self):
        vm_list = self.nova_client.servers.list()
        port_list = self.neutron_client.list_ports()

        flow_store = {
            "tenant_id": str(self.valid_network['tenant_id']),
            'image': self.valid_image.id,
            'flavor': self.valid_flavor.id,
            "port": self.port,
            "context": self.context.to_dict(),
            "erlang_cookie": str(uuid.uuid4()),
            "default_rabbit_user": 'rabbit',
            "default_rabbit_pass": str(uuid.uuid4()),
        }

        cluster_values = {
            "project_id": self.context.tenant_id,
            "name": "RabbitCluster",
            "network_id": self.valid_network['id'],
            "flavor": "1",
            "size": 10,
        }

        new_cluster = objects.Cluster(**cluster_values)
        new_cluster.create(self.context)

        nodes = objects.Node.get_nodes_by_cluster_id(self.context,
                                                     new_cluster.id)

        node_ids = []
        for node in nodes:
            node_ids.append(node.id)

        flow = create_cluster(new_cluster.id,
                              node_ids,
                              self.valid_network['id'],
                              self.management_network['id'])

        self.assertRaises(taskflow_exc.WrappedFailure, engines.run,
                          flow, store=flow_store)

        self.assertEqual(vm_list, self.nova_client.servers.list())
        self.assertEqual(port_list, self.neutron_client.list_ports())

    def test_create_cluster_invalid_user_network(self):
        invalid_network_id = str(uuid.uuid4())
        cluster_size = 3

        flow_store = {
            "tenant_id": str(self.valid_network['tenant_id']),
            'image': self.valid_image.id,
            'flavor': self.valid_flavor.id,
            "port": self.port,
            "context": self.context.to_dict(),
            "erlang_cookie": str(uuid.uuid4()),
            "default_rabbit_user": 'rabbit',
            "default_rabbit_pass": str(uuid.uuid4()),
        }

        cluster_values = {
            "project_id": self.context.tenant_id,
            "name": "RabbitCluster",
            "network_id": invalid_network_id,
            "flavor": "1",
            "size": cluster_size,
        }

        new_cluster = objects.Cluster(**cluster_values)
        new_cluster.create(self.context)

        nodes = objects.Node.get_nodes_by_cluster_id(self.context,
                                                     new_cluster.id)

        node_ids = []
        for node in nodes:
            node_ids.append(node.id)

        flow = create_cluster(new_cluster.id,
                              node_ids,
                              invalid_network_id,
                              self.management_network['id'])

        try:
            engines.run(flow, store=flow_store)
        except neutron_exceptions.NeutronClientException as err:
            # When an incorrect user network ID is given, the neutron client
            # returns a NeutronClientException.
            self.assertEqual(err.message,
                             "Network " + str(invalid_network_id) +
                             " could not be found.")
        else:
            self.fail("Expected taskflow_exc.WrappedFailure exception.")

    def test_create_cluster_anti_affinity(self):
        self.flags(cluster_node_anti_affinity=True, group="taskflow")

        flow_store = {
            "tenant_id": str(self.valid_network['tenant_id']),
            'image': self.valid_image.id,
            'flavor': self.valid_flavor.id,
            "port": self.port,
            "context": self.context.to_dict(),
            "erlang_cookie": str(uuid.uuid4()),
            "default_rabbit_user": 'rabbit',
            "default_rabbit_pass": str(uuid.uuid4()),
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
            node_ids.append(node.id)

        flow = create_cluster(new_cluster.id,
                              node_ids,
                              self.valid_network['id'],
                              self.management_network['id'])

        engines.run(flow, store=flow_store)

        nodes_after = objects.Node.get_nodes_by_cluster_id(self.context,
                                                           new_cluster.id)

        # check if the host_ids are different for cluster nodes
        host_ids = []
        for node in nodes_after:
            host_id = self.nova_client.servers.get(node.instance_id).host_id
            self.assertNotIn(host_id, host_ids)
            host_ids.append(host_id)

    def tearDown(self):
        for vm_id in self.new_vm_list:
            self.nova_client.servers.delete(vm_id)
        super(CreateClusterTests, self).tearDown()
