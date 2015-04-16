# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""Cue functional test utilities."""
from oslo.utils import timeutils

from cue.api.controllers.v1 import cluster
from cue.db.sqlalchemy import models
from cue import objects


def get_test_cluster(**kw):
    return {
        'id': kw.get('id', '1be26c0b-03f2-4d2e-ae87-c02d7f33c781'),
        'project_id': kw.get('project_id', '1234567890'),
        'name': kw.get('name', 'sample_cluster'),
        'network_id': kw.get('network_id',
                             '3dc26c0b-03f2-4d2e-ae87-c02d7f33c788'),
        'status': kw.get('status', 'BUILDING'),
        'flavor': kw.get('flavor', 'flavor1'),
        'size': kw.get('size', 1),
        'volume_size': kw.get('volume_size', 10),
        'deleted': kw.get('deleted', False),
        'created_at': kw.get('created_at', timeutils.utcnow()),
        'updated_at': kw.get('updated_at', timeutils.utcnow()),
        'deleted_at': kw.get('deleted_at', None),
    }


def create_api_test_cluster(**kw):
    """Create test Cluster api object and return this object.

    Function to be used to acquire an API Cluster object set with only required
    fields.  This would mimic a cluster object values received from REST API.

    :param kw: kwargs with overriding values for cluster's attributes.
    :returns: Test Cluster API object.
    """

    test_cluster = get_test_cluster(**kw)

    if isinstance(test_cluster['network_id'], (str, unicode)):
        test_cluster['network_id'] = [test_cluster['network_id']]

    cluster_parameters = {
        'name': test_cluster['name'],
        'network_id': test_cluster['network_id'],
        'flavor': test_cluster['flavor'],
        'size': str(test_cluster['size']),
        'volume_size': str(test_cluster['volume_size']),
    }

    new_cluster = cluster.Cluster(**cluster_parameters)

    return new_cluster


def create_api_test_cluster_all(**kw):
    """Create fully-populated test Cluster api object and return this object.

    Function to be used to acquire an API Cluster object with all fields set.

    :param kw: kwargs with overriding values for cluster's attributes.
    :returns: Test Cluster API object.
    """

    test_cluster = get_test_cluster(**kw)

    if isinstance(test_cluster['network_id'], (str, unicode)):
        test_cluster['network_id'] = [test_cluster['network_id']]

    cluster_parameters = {
        'name': test_cluster['name'],
        'network_id': test_cluster['network_id'],
        'flavor': test_cluster['flavor'],
        'size': test_cluster['size'],
        'volume_size': test_cluster['volume_size'],
        'id': test_cluster['id'],
        'project_id': test_cluster['project_id'],
        'status': test_cluster['status'],
        'created_at': test_cluster['created_at'],
        'updated_at': test_cluster['updated_at'],
    }

    new_cluster = cluster.Cluster(**cluster_parameters)

    return new_cluster


def create_db_test_cluster_from_objects_api(context, **kw):
    """Create test Cluster entry in DB from objects API and return Cluster

    DB object.  Function to be used to create test Cluster objects in the
    database.

    :param kw: kwargs with overriding values for cluster's attributes.
    :returns: Test Cluster DB object.

    """
    test_cluster = get_test_cluster(**kw)

    cluster_parameters = {
        'name': test_cluster['name'],
        'network_id': test_cluster['network_id'],
        'flavor': test_cluster['flavor'],
        'size': test_cluster['size'],
        'volume_size': test_cluster['volume_size'],
    }

    new_cluster = objects.Cluster(**cluster_parameters)

    new_cluster.create(context)

    # add some endpoints to each node in cluster
    cluster_nodes = objects.Node.get_nodes_by_cluster_id(context,
                                                         new_cluster.id)
    for i, node in enumerate(cluster_nodes):
        endpoint_value = {'node_id': node.id,
                          'uri': '10.0.0.' + str(i) + ':5672',
                          'type': 'AMQP'}
        endpoint = objects.Endpoint(**endpoint_value)
        endpoint.create(context)
        if i % 2:
            endpoint_value['uri'] = '10.0.' + str(i + 1) + '.0:5672'
            endpoint = objects.Endpoint(**endpoint_value)
            endpoint.create(context)

    return new_cluster


def create_db_test_cluster_model_object(context, **kw):
    """Create test Cluster DB model object.

    :param kw: kwargs with overriding values for cluster's attributes.
    :returns: Test Cluster DB model object.

    """
    test_cluster = get_test_cluster(**kw)

    cluster_parameters = {
        'name': test_cluster['name'],
        'network_id': test_cluster['network_id'],
        'flavor': test_cluster['flavor'],
        'size': test_cluster['size'],
        'volume_size': test_cluster['volume_size'],
        'id': test_cluster['id'],
        'project_id': test_cluster['project_id'],
        'status': test_cluster['status'],
        'deleted': test_cluster['deleted'],
        'created_at': test_cluster['created_at'],
        'updated_at': test_cluster['updated_at'],
        'deleted_at': test_cluster['deleted_at'],
    }

    new_cluster = models.Cluster()
    new_cluster.update(cluster_parameters)

    return new_cluster


def get_endpoints_in_cluster(context, cluster_id):
    nodes = objects.Node.get_nodes_by_cluster_id(context, cluster_id)
    all_endpoints = []
    for node in nodes:
        endpoints = objects.Endpoint.get_endpoints_by_node_id(context,
                                                              node.id)
        node_endpoints_dict = [obj_endpoint.as_dict()
                               for obj_endpoint in endpoints]

        all_endpoints.extend(node_endpoints_dict)

    return all_endpoints


def get_test_endpoint(**kw):
    return {
        'id': kw.get('id', '4ddedb63-ac35-48b7-84ef-f929fb6b065e'),
        'node_id': kw.get('node_id', '1be26c0b-03f2-4d2e-ae87-c02d7f33c781'),
        'uri': kw.get('uri', '10.0.0.1:5672'),
        'type': kw.get('type', 'AMQP')
    }


def get_test_node(**kw):
    return {
        'id': kw.get('id', '60abae56-b947-4401-99ad-29e4643c6249'),
        'cluster_id': kw.get('cluster_id',
                             '1be26c0b-03f2-4d2e-ae87-c02d7f33c781'
                             ),
        'instance_id': kw.get('instance_id',
                              'b7cf7433-60f7-4d09-a759-cee12d8a3cb3'),
        'flavor': kw.get('flavor', 'flavor1'),
        'status': kw.get('status', 'BUILDING'),
        'created_at': kw.get('created_at', timeutils.utcnow()),
        'updated_at': kw.get('updated_at', timeutils.utcnow()),
        'deleted_at': kw.get('deleted_at', None)
    }


def create_object_cluster(context, **kw):
    """Create test Cluster entry in DB from objects API and return Cluster

    object.
    """
    test_cluster_dict = get_test_cluster(**kw)
    new_cluster = objects.Cluster(**test_cluster_dict)
    new_cluster.create(context)
    return new_cluster