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

from oslo.config import cfg
from oslo_log import log as logging
from keystoneclient.auth.identity.generic import password
from keystoneclient import session
from stevedore import extension

from cue.common.i18n import _
from cue.common.i18n import _LW

LOG = logging.getLogger(__name__)

_mngr = None
_session = None


auth_opts = [
    cfg.StrOpt('username', help='Username'),
    cfg.StrOpt('auth_url', help='Auth url'),
    cfg.StrOpt('password', help='Password'),
    cfg.StrOpt('tenant_name', help='Tenant')
]

default_clients_opts = [
    cfg.StrOpt('endpoint_type',
               default='publicURL',
               help=_(
                   'Type of endpoint in Identity service catalog to use '
                   'for communication with the OpenStack service.')),
    cfg.StrOpt('ca_file',
               help=_('Optional CA cert file to use in SSL connections.')),
    cfg.StrOpt('cert_file',
               help=_('Optional PEM-formatted certificate chain file.')),
    cfg.StrOpt('key_file',
               help=_('Optional PEM-formatted file that contains the '
                      'private key.')),
    cfg.BoolOpt('insecure',
                default=False,
                help=_("If set, then the server's certificate will not "
                       "be verified."))]


for i in ["cinder", "neutron", "nova"]:
    group = 'clients:%s' % i
    cfg.CONF.register_opts(default_clients_opts, group=group)

cfg.CONF.register_opts(auth_opts, group='clients')
cfg.CONF.register_opts(default_clients_opts, group='clients')


def get_client_option(client, option):
    # look for the option in the [clients_${client}] section
    # unknown options raise cfg.NoSuchOptError
    try:
        group_name = 'clients_' + client
        cfg.CONF.import_opt(option, 'cue.clients',
                            group=group_name)
        v = getattr(getattr(cfg.CONF, group_name), option)
        if v is not None:
            return v
    except cfg.NoSuchGroupError:
        pass  # do not error if the client is unknown
    # look for the option in the generic [clients] section
    #cfg.CONF.import_opt(option, 'cue.clients', group='clients')
    return getattr(cfg.CONF.clients, option)


class Manager(object):
    '''
    Convenience class to create and cache client instances.
    '''

    def __init__(self):
        self._clients = {}
        self._client_plugins = {}
        self._mngr = extension.ExtensionManager(
            namespace='cue.clients',
            invoke_on_load=False,
            verify_requirements=True)

    @property
    def session(self):
        # FIXME(jamielennox): This session object is essentially static as the
        # options won't change. Further it is allowed to be shared by multiple
        # authentication requests so there is no reason to construct it fresh
        # for every client plugin. It should be global and shared amongst them.
        global _session
        if _session is None:
            auth = password.Password(
                username=cfg.CONF.clients.username,
                password=cfg.CONF.clients.password,
                tenant_name=cfg.CONF.clients.tenant_name,
                auth_url=cfg.CONF.clients.auth_url
            )

            o = {'cacert': get_client_option('keystone', 'ca_file'),
                 'insecure': get_client_option('keystone', 'insecure'),
                 'cert': get_client_option('keystone', 'cert_file'),
                 'key': get_client_option('keystone', 'key_file')}

            _session = session.Session.construct(o)
            _session.auth = auth

        return _session

    def client_plugin(self, name):
        if name in self._client_plugins:
            return self._client_plugins[name]
        if name in self._mngr.names():
            client_plugin = self._mngr[name].plugin(self.session)
            self._client_plugins[name] = client_plugin
            return client_plugin

    def client(self, name):
        client_plugin = self.client_plugin(name)
        if client_plugin:
            return client_plugin.client()

        if name in self._clients:
            return self._clients[name]
        # call the local method _<name>() if a real client plugin
        # doesn't exist
        method_name = '_%s' % name
        if callable(getattr(self, method_name, None)):
            client = getattr(self, method_name)()
            self._clients[name] = client
            return client
        LOG.warn(_LW('Requested client "%s" not found'), name)

    def __getitem__(self, key):
        return self.client(key)

    @property
    def auth_token(self):
        # Always use the auth_token from the keystone() client, as
        # this may be refreshed if the context contains credentials
        # which allow reissuing of a new token before the context
        # auth_token expiry (e.g trust_id or username/password)
        return self.client('keystone').auth_token

    def url_for(self, **kwargs):
        return self.client('keystone').url_for(**kwargs)


def init():
    global _mngr
    if _mngr is None:
        _mngr = Manager()


def get_manager():
    global _mngr
    if not _mngr:
        init()
    return _mngr
