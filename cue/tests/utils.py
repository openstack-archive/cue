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
"""Cue test utilities."""

from oslo.utils import timeutils

from cue.api.controllers import v1
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

    cluster = get_test_cluster(**kw)

    cluster_parameters = {
        'name': cluster['name'],
        'network_id': cluster['network_id'],
        'flavor': cluster['flavor'],
        'size': str(cluster['size']),
        'volume_size': str(cluster['volume_size']),
    }

    new_cluster = v1.Cluster(**cluster_parameters)

    return new_cluster


def create_api_test_cluster_all(**kw):
    """Create fully-populated test Cluster api object and return this object.

    Function to be used to acquire an API Cluster object with all fields set.

    :param kw: kwargs with overriding values for cluster's attributes.
    :returns: Test Cluster API object.
    """

    cluster = get_test_cluster(**kw)

    cluster_parameters = {
        'name': cluster['name'],
        'network_id': cluster['network_id'],
        'flavor': cluster['flavor'],
        'size': cluster['size'],
        'volume_size': cluster['volume_size'],
        'id': cluster['id'],
        'project_id': cluster['project_id'],
        'status': cluster['status'],
        'created_at': cluster['created_at'],
        'updated_at': cluster['updated_at'],
    }

    new_cluster = v1.Cluster(**cluster_parameters)

    return new_cluster


def create_db_test_cluster_from_objects_api(**kw):
    """Create test Cluster entry in DB from objects API and return Cluster

    DB object.  Function to be used to create test Cluster objects in the
    database.

    :param kw: kwargs with overriding values for cluster's attributes.
    :returns: Test Cluster DB object.

    """
    cluster = get_test_cluster(**kw)

    cluster_parameters = {
        'name': cluster['name'],
        'network_id': cluster['network_id'],
        'flavor': cluster['flavor'],
        'size': cluster['size'],
        'volume_size': cluster['volume_size'],
    }

    new_cluster = objects.Cluster(**cluster_parameters)

    project_id = cluster['project_id']

    new_cluster.create_cluster(project_id)

    return new_cluster


def create_db_test_cluster_model_object(**kw):
    """Create test Cluster DB model object.

    :param kw: kwargs with overriding values for cluster's attributes.
    :returns: Test Cluster DB model object.

    """
    cluster = get_test_cluster(**kw)

    cluster_parameters = {
        'name': cluster['name'],
        'network_id': cluster['network_id'],
        'flavor': cluster['flavor'],
        'size': cluster['size'],
        'volume_size': cluster['volume_size'],
        'id': cluster['id'],
        'project_id': cluster['project_id'],
        'status': cluster['status'],
        'deleted': cluster['deleted'],
        'created_at': cluster['created_at'],
        'updated_at': cluster['updated_at'],
        'deleted_at': cluster['deleted_at'],
    }

    new_cluster = models.Cluster()
    new_cluster.update(cluster_parameters)

    return new_cluster