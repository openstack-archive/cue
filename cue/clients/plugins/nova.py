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

import logging

from novaclient import client as nc
from novaclient import exceptions
from novaclient import shell as novashell

from cue import clients
from cue.clients import plugin
from cue.common.i18n import _  # noqa
from cue.common.i18n import _LW  # noqa

LOG = logging.getLogger(__name__)


class NovaClientPlugin(plugin.ClientPlugin):

    deferred_server_statuses = ['BUILD',
                                'HARD_REBOOT',
                                'PASSWORD',
                                'REBOOT',
                                'RESCUE',
                                'RESIZE',
                                'REVERT_RESIZE',
                                'SHUTOFF',
                                'SUSPENDED',
                                'VERIFY_RESIZE']

    exceptions_module = exceptions

    def _create(self):
        computeshell = novashell.OpenStackComputeShell()
        extensions = computeshell._discover_extensions("1.1")

        endpoint_type = clients.get_client_option('nova', 'endpoint_type')
        args = {
            'session': self.session,
            'service_type': 'compute',
            'username': None,
            'api_key': None,
            'extensions': extensions,
            'endpoint_type': endpoint_type,
            #'http_log_debug': clients._get_client_option('nova',
            #                                          'http_log_debug'),
            'cacert': clients.get_client_option('nova', 'ca_file'),
            'insecure': clients.get_client_option('nova', 'insecure'),
        }

        client = nc.Client(1.1, **args)

        #management_url = self.url_for(service_type='compute',
        #                              endpoint_type=endpoint_type)
        #client.client.auth_token = self.auth_token
        #client.client.management_url = management_url

        return client

    def is_not_found(self, ex):
        return isinstance(ex, exceptions.NotFound)

    def is_over_limit(self, ex):
        return isinstance(ex, exceptions.OverLimit)

    def is_bad_request(self, ex):
        return isinstance(ex, exceptions.BadRequest)

    def is_conflict(self, ex):
        return isinstance(ex, exceptions.Conflict)

    def is_unprocessable_entity(self, ex):
        http_status = (getattr(ex, 'http_status', None) or
                       getattr(ex, 'code', None))
        return (isinstance(ex, exceptions.ClientException) and
                http_status == 422)
