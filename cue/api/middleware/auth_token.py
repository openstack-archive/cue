# -*- encoding: utf-8 -*-
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

import re

from keystonemiddleware import auth_token

from cue.common import exception
from cue.common.i18n import _  # noqa
from cue.common import utils
from cue.openstack.common import log

LOG = log.getLogger(__name__)


class AuthTokenMiddleware(auth_token.AuthProtocol):
    """A wrapper on Keystone auth_token middleware.

    Does not perform verification of authentication tokens
    for public routes in the API.

    """
    def __init__(self, app, conf, public_api_routes=[]):
        route_pattern_tpl = '%s(\.json|\.xml)?$'

        try:
            self.public_api_routes = [re.compile(route_pattern_tpl % route_tpl)
                                      for route_tpl in public_api_routes]
        except re.error as e:
            msg = _('Cannot compile public API routes: %s') % e

            LOG.error(msg)
            raise exception.ConfigInvalid(error_msg=msg)

        super(AuthTokenMiddleware, self).__init__(app, conf)

    def __call__(self, env, start_response):
        path = utils.safe_rstrip(env.get('PATH_INFO'), '/')

        # The information whether the API call is being performed against the
        # public API is required for some other components. Saving it to the
        # WSGI environment is reasonable thereby.
        env['is_public_api'] = any(map(lambda pattern: re.match(pattern, path),
                                       self.public_api_routes))

        if env['is_public_api']:
            return self._app(env, start_response)

        return super(AuthTokenMiddleware, self).__call__(env, start_response)
