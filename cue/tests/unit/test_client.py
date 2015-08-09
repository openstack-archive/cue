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

import mock
from oslo_config import fixture as config_fixture

from cue import client
from cue.tests.unit import base


class TestClient(base.UnitTestCase):

    def setUp(self):

        super(TestClient, self).setUp()

        # setup config fixture
        self.CONF = config_fixture.Config()
        self.useFixture(self.CONF)

    def tearDown(self):

        super(TestClient, self).tearDown()
        self.CONF.reset()

    @mock.patch('keystoneclient.auth.identity.v2.Password')
    def test_get_auth_v2(self, mock_auth_v2):
        """Test cue.client get_auth_v2.

        Asserts that the keystone auth password is called.
        """

        os_auth_url = "http://localhost:5000/v2.0"
        os_username = "test_user"
        os_password = "test_password"
        os_tenant_name = "test_tenant"
        self.CONF.config(os_auth_url=os_auth_url,
                         os_username=os_username,
                         os_password=os_password,
                         os_tenant_name=os_tenant_name,
                         group="openstack")
        client.get_auth_v2()
        mock_auth_v2.assert_called_once_with(auth_url=os_auth_url,
                                             password=os_password,
                                             tenant_name=os_tenant_name,
                                             username=os_username)

    @mock.patch('keystoneclient.auth.identity.v3.Password')
    def test_get_auth_v3(self, mock_auth_v3):
        """Test cue.client get_auth_v3.

        Asserts that the keystone auth password is called.
        """

        os_auth_url = "http://localhost:5000/v3"
        os_username = "test_user"
        os_password = "test_password"
        os_project_name = "test_project"
        os_project_domain_name = "test_domain"
        os_user_domain_name = "test_domain"
        self.CONF.config(os_auth_url=os_auth_url,
                         os_username=os_username,
                         os_password=os_password,
                         os_project_name=os_project_name,
                         os_project_domain_name=os_project_domain_name,
                         os_user_domain_name=os_user_domain_name,
                         group="openstack")
        client.get_auth_v3()
        mock_auth_v3.assert_called_once_with(
            auth_url=os_auth_url,
            password=os_password,
            project_domain_name=os_project_domain_name,
            project_name=os_project_name,
            user_domain_name=os_user_domain_name,
            username=os_username)

    @mock.patch('keystoneclient.session.Session')
    @mock.patch('cue.client.get_auth_v2')
    def test_get_keystone_session_v2(self, mock_auth_v2, mock_ks_session):
        """Test cue.client get_keystone_session.

        Asserts that the keystone session and client get_auth_v2 is called.
        """

        os_auth_version = "2.0"
        self.CONF.config(os_auth_version=os_auth_version,
                         group="openstack")
        client.get_keystone_session()
        mock_auth_v2.assert_called_once_with()
        mock_ks_session.assert_called_once_with(auth=mock_auth_v2())

    @mock.patch('keystoneclient.session.Session')
    @mock.patch('cue.client.get_auth_v3')
    def test_get_keystone_session_v3(self, mock_auth_v3, mock_ks_session):
        """Test cue.client get_keystone_session.

        Asserts that the keystone session and client get_auth_v3 is called.
        """

        os_auth_version = "3"
        self.CONF.config(os_auth_version=os_auth_version,
                         group="openstack")
        client.get_keystone_session()
        mock_auth_v3.assert_called_once_with()
        mock_ks_session.assert_called_once_with(auth=mock_auth_v3())
