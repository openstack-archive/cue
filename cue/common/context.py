# -*- encoding: utf-8 -*-
# Copyright 2014-2015 Hewlett-Packard Development Company, L.P.
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

from oslo_context import context


class RequestContext(context.RequestContext):
    """Extends security contexts from the OpenStack common library."""

    def __init__(self, auth_token=None, user=None, tenant=None, domain=None,
                 user_domain=None, project_domain=None, is_admin=False,
                 read_only=False, show_deleted=False, request_id=None,
                 resource_uuid=None, overwrite=True, roles=None,
                 is_public_api=False, domain_id=None, domain_name=None):
        """Stores several additional request parameters:

        :param roles:
        :param domain_id: The ID of the domain.
        :param domain_name: The name of the domain.
        :param is_public_api: Specifies whether the request should be processed
                              without authentication.

        """
        super(RequestContext, self).__init__(auth_token=auth_token, user=user,
                                             tenant=tenant, domain=domain,
                                             user_domain=user_domain,
                                             project_domain=project_domain,
                                             is_admin=is_admin,
                                             read_only=read_only,
                                             show_deleted=show_deleted,
                                             request_id=request_id,
                                             resource_uuid=resource_uuid,
                                             overwrite=overwrite)

        self.roles = roles or []
        self.is_public_api = is_public_api
        self.domain_id = domain_id
        self.domain_name = domain_name

    @property
    def project_id(self):
        return self.tenant

    @property
    def tenant_id(self):
        return self.tenant

    @tenant_id.setter
    def tenant_id(self, tenant_id):
        self.tenant = tenant_id

    @property
    def user_id(self):
        return self.user

    @user_id.setter
    def user_id(self, user_id):
        self.user = user_id

    @classmethod
    def from_dict(cls, values):
        if 'user_identity' in values:
            del values['user_identity']
        return cls(**values)

    def to_dict(self):
        values = super(RequestContext, self).to_dict()
        values.update({
            "roles": self.roles,
            "is_public_api": self.is_public_api,
            "domain_id": self.domain_id,
            "domain_name": self.domain_name
        })
        return values
