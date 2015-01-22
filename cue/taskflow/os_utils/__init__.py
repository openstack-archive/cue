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

import cinderclient.client as CinderClient
import neutronclient.neutron.client as NeutronClient
import novaclient.client as NovaClient

neutron_version = '2.0'
neutron_client_parameters = {
    'username': 'admin',
    'password': 'messina',
    'tenant_name': 'demo',
    'auth_url': 'http://192.168.131.136:5000/v2.0'
}


def nova_client():
    return NovaClient.Client(2,
                             'admin',
                             'secrete',
                             'demo',
                             'http://192.168.41.183:5000/v2.0')


def cinder_client():
    return CinderClient.Client('1',
                               'admin',
                               'secrete',
                               'demo',
                               'http://192.168.41.183:5000/v2.0')


def neutron_client():
    return NeutronClient.Client(neutron_version,
                                **neutron_client_parameters)
