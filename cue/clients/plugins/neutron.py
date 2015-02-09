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

from neutronclient.common import exceptions
from neutronclient.v2_0 import client as nc

from cue import clients
from cue.clients import plugins


class NeutronClientPlugin(plugins.ClientPlugin):

    exceptions_module = exceptions

    def _create(self):
        endpoint_type = clients.get_client_option('neutron', 'endpoint_type')

        args = {
            'service_type': 'network',
            'endpoint_type': endpoint_type,
            'ca_cert': clients.get_client_option('neutron', 'ca_file'),
            'insecure': clients.get_client_option('neutron', 'insecure'),
            'session': self.session
        }

        return nc.Client(**args)

    def is_not_found(self, ex):
        if isinstance(ex, (exceptions.NotFound,
                           exceptions.NetworkNotFoundClient,
                           exceptions.PortNotFoundClient)):
            return True
        return (isinstance(ex, exceptions.NeutronClientException) and
                ex.status_code == 404)

    def is_conflict(self, ex):
        bad_conflicts = (exceptions.OverQuotaClient,)
        return (isinstance(ex, exceptions.Conflict) and
                not isinstance(ex, bad_conflicts))

    def is_over_limit(self, ex):
        if not isinstance(ex, exceptions.NeutronClientException):
            return False
        return ex.status_code == 413

    def is_no_unique(self, ex):
        return isinstance(ex, exceptions.NeutronClientNoUniqueMatch)

    def _resolve(self, props, key, id_key, key_type):
        if props.get(key):
            props[id_key] = self.find_neutron_resource(
                props, key, key_type)
            props.pop(key)
        return props[id_key]

    def resolve_network(self, props, net_key, net_id_key):
        return self._resolve(props, net_key, net_id_key, 'network')

    def resolve_subnet(self, props, subnet_key, subnet_id_key):
        return self._resolve(props, subnet_key, subnet_id_key, 'subnet')

    def resolve_router(self, props, router_key, router_id_key):
        return self._resolve(props, router_key, router_id_key, 'router')

    def resolve_port(self, props, port_key, port_id_key):
        return self._resolve(props, port_key, port_id_key, 'port')

    def network_id_from_subnet_id(self, subnet_id):
        subnet_info = self.client().show_subnet(subnet_id)
        return subnet_info['subnet']['network_id']
