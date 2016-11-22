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

import json

from tempest.lib import auth
from tempest.lib.common import rest_client
from tempest.lib.services.compute import tenant_networks_client

from tests.integration.common import config


CONF = config.get_config()


class BaseMessageQueueClient(rest_client.RestClient):
    """This class is used for building Cue api clients.

    It extends the Openstack RestClient class, which provides a base layer for
    wrapping outgoing http requests in keystone auth as well as providing
    response code checking and error handling. It obtains the keystone
    credentials from the configuration.
    """

    def __init__(self):

        auth_provider = _get_keystone_auth_provider()
        super(BaseMessageQueueClient, self).__init__(
            auth_provider=auth_provider,
            service='message-broker',
            region='RegionOne',
        )
        self.private_network = self._get_network('private')

    def _get_network(self, label):
        network_client = tenant_networks_client.TenantNetworksClient(
            _get_keystone_auth_provider(),
            'compute',
            'RegionOne')
        networks = network_client.list_tenant_networks()['networks']
        return [network for network in networks
                if network['label'] == label][0]


class ServerClient(rest_client.RestClient):
    """This class is used for querying Nova servers.

    It extends the Openstack RestClient class, which provides a base layer for
    wrapping outgoing http requests in keystone auth as well as providing
    response code checking and error handling. It obtains the keystone
    credentials from the configuration.
    """

    def __init__(self):

        auth_provider = _get_keystone_auth_provider(username='admin',
                                                    project_name='admin')
        super(ServerClient, self).__init__(
            auth_provider=auth_provider,
            service='compute',
            region='RegionOne',
        )

    def get_cluster_nodes(self, cluster_id=None):
        """Get all server nodes of a cluster

        :param cluster_id: The cluster to get the nodes from
        """

        url = 'servers/detail'
        if cluster_id:
            url += '?name=%s' % cluster_id

        resp, body = self.get(url)
        body = json.loads(body)
        return rest_client.ResponseBody(resp, body)

    def get_console_log(self, server_id):
        """Get the console node for a server

        :param server_id: The server to get the console log from
        """
        post_body = json.dumps({"os-getConsoleOutput": {}})
        resp, body = self.post('servers/%s/action' % str(server_id),
                               post_body)
        body = json.loads(body)['output']

        return rest_client.ResponseBodyData(resp, body)

    def stop_server(self, server_id):
        """Stops the specified server

        :param server_id: The UUID for the server.
        """
        post_body = json.dumps({"os-stop": None})
        resp, body = self.post('servers/%s/action' % str(server_id),
                               post_body)

        return rest_client.ResponseBodyData(resp, body)


def _get_keystone_auth_provider(username=None, password=None,
                                project_name=None, user_domain_name=None,
                                project_domain_name=None):

    keystone_v3 = CONF.identity.auth_version is '3'
    if keystone_v3:
        creds = auth.KeystoneV3Credentials(
            username=username or CONF.identity.username,
            password=password or CONF.identity.password,
            project_name=project_name or CONF.identity.project_name,
            user_domain_name=(user_domain_name or
                              CONF.identity.user_domain_name),
            project_domain_name=(project_domain_name or
                                 CONF.identity.project_domain_name)
        )
        auth_provider = auth.KeystoneV3AuthProvider(creds,
                                                    CONF.identity.uri)
    else:
        creds = auth.KeystoneV2Credentials(
            username=username or CONF.identity.username,
            password=password or CONF.identity.password,
            tenant_name=project_name or CONF.identity.project_name,
        )
        auth_provider = auth.KeystoneV2AuthProvider(creds,
                                                    CONF.identity.uri)
    auth_provider.fill_credentials()
    return auth_provider
