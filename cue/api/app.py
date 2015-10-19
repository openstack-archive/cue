# -*- encoding: utf-8 -*-

# Copyright © 2012 New Dream Network, LLC (DreamHost)
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

from oslo_config import cfg
from oslo_middleware import cors as cors_middleware
import pecan

from cue.api import acl
from cue.api import config
from cue.api import hooks
from cue.api import middleware
from cue.common import policy

auth_opts = [
    cfg.StrOpt('auth_strategy',
        default='keystone',
        help='Method to use for authentication: noauth or keystone.'),
    ]

API_OPTS = [
    cfg.BoolOpt('pecan_debug', default=False,
                help='Pecan HTML Debug Interface'),
]

cfg.CONF.register_opts(auth_opts)
cfg.CONF.register_opts(API_OPTS, group='api')


def list_opts():
    return [('DEFAULT', auth_opts), ('api', API_OPTS)]


def get_pecan_config():
    # Set up the pecan configuration
    filename = config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)


def setup_app(pecan_config=None, extra_hooks=None):
    policy.init()
    app_hooks = [hooks.ConfigHook(),
                 #hooks.DBHook(),
                 hooks.ContextHook(pecan_config.app.acl_public_routes),
                 #hooks.RPCHook(),
                 #hooks.NoExceptionTracebackHook()
                 ]
    if extra_hooks:
        app_hooks.extend(extra_hooks)

    if not pecan_config:
        pecan_config = get_pecan_config()

    pecan.configuration.set_config(dict(pecan_config), overwrite=True)
    app = pecan.make_app(
        pecan_config.app.root,
        static_root=pecan_config.app.static_root,
        debug=cfg.CONF.api.pecan_debug,
        force_canonical=getattr(pecan_config.app, 'force_canonical', True),
        hooks=app_hooks,
        wrap_app=middleware.ParsableErrorMiddleware,
    )

    if pecan_config.app.enable_acl:
        app = acl.install(app, cfg.CONF, pecan_config.app.acl_public_routes)

    # Create a CORS wrapper, and attach ironic-specific defaults that must be
    # included in all CORS responses.
    app = cors_middleware.CORS(app, cfg.CONF)
    app.set_latent(
        allow_headers=['X-Auth-Token', 'X-Server-Management-Url'],
        allow_methods=['GET', 'PUT', 'POST', 'DELETE', 'PATCH'],
        expose_headers=['X-Auth-Token', 'X-Server-Management-Url']
    )

    return app


class VersionSelectorApplication(object):
    def __init__(self):
        pc = get_pecan_config()
        pc.app.enable_acl = (cfg.CONF.auth_strategy == 'keystone')
        self.v1 = setup_app(pecan_config=pc)

    def __call__(self, environ, start_response):
        return self.v1(environ, start_response)
