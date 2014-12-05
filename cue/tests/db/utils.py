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

from cue.db import api as db_api


def get_test_cluster(**kw):
    return {
        'id': kw.get('id', '1be26c0b-03f2-4d2e-ae87-c02d7f33c781'),
        'project_id': kw.get('project_id', '1234567890'),
        'name': kw.get('name', 'sample_cluster'),
        'nic': kw.get('nic', '3dc26c0b-03f2-4d2e-ae87-c02d7f33c788'),
        'status': kw.get('status', 'BUILDING'),
        'volume_size': kw.get('volume_size', 10),
        'created_at': kw.get('created_at', timeutils.utcnow()),
        'updated_at': kw.get('updated_at', timeutils.utcnow()),
    }


def create_test_cluster(**kw):
    """Create test Cluster entry in DB and return Cluster DB object.

    Function to be used to create test Cluster objects in the database.

    :param kw: kwargs with overriding values for cluster's attributes.
    :returns: Test Cluster DB object.

    """
    cluster = get_test_cluster(**kw)

    return db_api.create_cluster(cluster['project_id'], cluster['name'],
                                 cluster['nic'], cluster['volume_size'],
                                 "flavor1", 1)
