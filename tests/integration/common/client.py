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

from tempest.services.compute.json import tenant_networks_client
from tempest_lib import auth
from tempest_lib.common import rest_client

from tests.integration.common import config


CONF = config.get_config()


class BaseMessageQueueClient(rest_client.RestClient):

    def __init__(self):

        auth_provider = self._get_keystone_auth_provider()
        super(BaseMessageQueueClient, self).__init__(
            auth_provider=auth_provider,
            service='message_queue',
            region='RegionOne',
        )
        self.private_network = self._get_network('private')

    def _get_network(self, label):
        network_client = tenant_networks_client.TenantNetworksClientJSON(
            self._get_keystone_auth_provider(),
            'compute',
            'RegionOne')
        networks = network_client.list_tenant_networks()
        return [network for network in networks
                if network['label'] == label][0]

    def _get_keystone_auth_provider(self):
        creds = auth.KeystoneV2Credentials(
            username=CONF.identity.username,
            password=CONF.identity.password,
            tenant_name=CONF.identity.tenant_name,
        )
        auth_provider = auth.KeystoneV2AuthProvider(creds,
                                                    CONF.identity.uri)
        auth_provider.fill_credentials()
        return auth_provider
