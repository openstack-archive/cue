#
# Copyright 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
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
"""Base classes for API tests.
"""

from oslo.config import cfg
from oslo.config import fixture as fixture_config
import pecan
import pecan.testing

from cue.api import hooks
from cue.tests.functional import base

OPT_GROUP_NAME = 'keystone_authtoken'
cfg.CONF.import_group(OPT_GROUP_NAME, "keystonemiddleware.auth_token")


class APITest(base.FunctionalTestCase):
    """Used for functional tests of Pecan controllers.

    Used in case when you need to test your literal application and its
    integration with the framework.
    """

    PATH_PREFIX = ''

    def setUp(self):
        super(APITest, self).setUp()
        self.CONF = self.useFixture(fixture_config.Config()).conf

        self.CONF.set_override("auth_version", "v2.0",
                               group=OPT_GROUP_NAME)
        # self.CONF.set_override("policy_file",
        #                        self.path_get('etc/cue/policy.json'))
        self.app = self._make_app()
        self.auth_headers = {'X-User-Id': str(self.context.user_id),
                             'X-Project-Id': str(self.context.project_id)}

    def _make_app(self, enable_acl=False):
        # Determine where we are so we can set up paths in the config
        root_dir = self.path_get()

        self.config = {
            'app': {
                'root': 'cue.api.controllers.root.RootController',
                'modules': ['cue.api'],
                'hooks': [hooks.ContextHook],
                'static_root': '%s/public' % root_dir,
                'template_path': '%s/cue/api/templates' % root_dir,
                'enable_acl': enable_acl,
                'acl_public_routes': ['/', '/v1'],
            },
            'wsme': {
                'debug': True,
            },
        }

        return pecan.testing.load_test_app(self.config)

    def tearDown(self):
        super(APITest, self).tearDown()
        pecan.set_config({}, overwrite=True)

    def put_json(self, path, params, expect_errors=False, headers=None,
                 extra_environ=None, status=None):
        """Sends simulated HTTP PUT request to Pecan test app.

        :param path: url path of target service
        :param params: content for wsgi.input of request
        :param expect_errors: boolean value whether an error is expected based
                              on request
        :param headers: A dictionary of headers to send along with the request
        :param extra_environ: A dictionary of environ variables to send along
                              with the request
        :param status: Expected status code of response
        """
        return self.post_json(path=path, params=params,
                              expect_errors=expect_errors,
                              headers=headers, extra_environ=extra_environ,
                              status=status, method="put")

    def post_json(self, path, params, expect_errors=False, headers=None,
                  method="post", extra_environ=None, status=None):
        """Sends simulated HTTP POST request to Pecan test app.

        :param path: url path of target service
        :param params: content for wsgi.input of request
        :param expect_errors: boolean value whether an error is expected based
                              on request
        :param headers: A dictionary of headers to send along with the request
        :param method: Request method type. Appropriate method function call
                       should be used rather than passing attribute in.
        :param extra_environ: A dictionary of environ variables to send along
                              with the request
        :param status: Expected status code of response
        """
        full_path = self.PATH_PREFIX + path
        response = getattr(self.app, "%s_json" % method)(
            str(full_path),
            params=params,
            headers=headers,
            status=status,
            extra_environ=extra_environ,
            expect_errors=expect_errors
        )
        return response

    def delete(self, path, expect_errors=False, headers=None,
               extra_environ=None, status=None):
        """Sends simulated HTTP DELETE request to Pecan test app.

        :param path: url path of target service
        :param expect_errors: boolean value whether an error is expected based
                              on request
        :param headers: A dictionary of headers to send along with the request
        :param extra_environ: A dictionary of environ variables to send along
                              with the request
        :param status: Expected status code of response
        """
        full_path = self.PATH_PREFIX + path
        response = self.app.delete(str(full_path),
                                   headers=headers,
                                   status=status,
                                   extra_environ=extra_environ,
                                   expect_errors=expect_errors)
        return response

    def get_json(self, path, expect_errors=False, headers=None,
                 extra_environ=None, q=None, groupby=None, status=None,
                 override_params=None, **params):
        """Sends simulated HTTP GET request to Pecan test app.

        :param path: url path of target service
        :param expect_errors: boolean value whether an error is expected based
                              on request
        :param headers: A dictionary of headers to send along with the request
        :param extra_environ: A dictionary of environ variables to send along
                              with the request
        :param q: list of queries consisting of: field, value, op, and type
                  keys
        :param groupby: list of fields to group by
        :param status: Expected status code of response
        :param override_params: literally encoded query param string
        :param params: content for wsgi.input of request
        """
        q = q or []
        groupby = groupby or []
        full_path = self.PATH_PREFIX + path
        if override_params:
            all_params = override_params
        else:
            query_params = {'q.field': [],
                            'q.value': [],
                            'q.op': [],
                            'q.type': [],
                            }
            for query in q:
                for name in ['field', 'op', 'value', 'type']:
                    query_params['q.%s' % name].append(query.get(name, ''))
            all_params = {}
            all_params.update(params)
            if q:
                all_params.update(query_params)
            if groupby:
                all_params.update({'groupby': groupby})
        response = self.app.get(full_path,
                                params=all_params,
                                headers=headers,
                                extra_environ=extra_environ,
                                expect_errors=expect_errors,
                                status=status)
        if not expect_errors:
            response = response.json
        return response
