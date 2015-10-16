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

from keystoneclient.auth.identity import v2 as keystone_v2_auth
from keystoneclient.auth.identity import v3 as keystone_v3_auth
from keystoneclient import session as keystone_session
import neutronclient.neutron.client as NeutronClient
import novaclient.client as NovaClient
from oslo_config import cfg
from oslo_log import log as logging


LOG = logging.getLogger(__name__)
CONF = cfg.CONF


OS_OPTS = [
    cfg.StrOpt('os_region_name',
               help='Region name',
               default=None),
    cfg.StrOpt('os_username',
               help='Openstack Username',
               default=None),
    cfg.StrOpt('os_password',
               help='Openstack Password',
               default=None),
    cfg.StrOpt('os_auth_version',
               help='Openstack authentication version',
               choices=('2.0', '3'),
               default='3'),
    cfg.StrOpt('os_auth_url',
               help='Openstack Authentication (Identity) URL',
               default=None),
    cfg.StrOpt('os_key_name',
               help='SSH key to be provisioned to cue VMs',
               default=None),
    cfg.StrOpt('os_availability_zone',
               help='Default availability zone to provision cue VMs',
               default=None),
    cfg.BoolOpt('os_insecure',
                help='Openstack insecure',
                default=False),
    cfg.StrOpt('os_cacert',
               help='Openstack cacert',
               default=None),
    cfg.StrOpt('os_project_name',
               help='Openstack project name',
               default=None),
    cfg.StrOpt('os_project_domain_name',
               help='Openstack project domain name',
               default=None),
    cfg.StrOpt('os_user_domain_name',
               help='Openstack user domain name',
               default=None),
    cfg.StrOpt('os_endpoint_type',
               help='Openstack endpoint type (publicURL/internalURL/adminURL)',
               default='publicURL'),
]

opt_group = cfg.OptGroup(
    name='openstack',
    title='Options for Openstack.'
)

CONF.register_group(opt_group)
CONF.register_opts(OS_OPTS, group=opt_group)


def nova_client():
    keystoneSession = get_keystone_session()
    return NovaClient.Client(2,
                             session=keystoneSession,
                             auth_url=CONF.openstack.os_auth_url,
                             region_name=CONF.openstack.os_region_name,
                             insecure=CONF.openstack.os_insecure,
                             cacert=CONF.openstack.os_cacert,
                             endpoint_type=CONF.openstack.os_endpoint_type,
                             )


def neutron_client():
    keystoneSession = get_keystone_session()
    return NeutronClient.Client('2.0',
                                session=keystoneSession,
                                auth_url=CONF.openstack.os_auth_url,
                                region_name=CONF.openstack.os_region_name,
                                insecure=CONF.openstack.os_insecure,
                                ca_cert=CONF.openstack.os_cacert,
                                endpoint_type=CONF.openstack.os_endpoint_type,
                                )


def get_auth_v2():
    auth_url = CONF.openstack.os_auth_url
    username = CONF.openstack.os_username
    password = CONF.openstack.os_password
    tenant_name = CONF.openstack.os_project_name
    return keystone_v2_auth.Password(auth_url=auth_url,
                                     username=username,
                                     password=password,
                                     tenant_name=tenant_name,
                                     )


def get_auth_v3():
    auth_url = CONF.openstack.os_auth_url
    username = CONF.openstack.os_username
    password = CONF.openstack.os_password
    project_name = CONF.openstack.os_project_name
    project_domain_name = CONF.openstack.os_project_domain_name
    user_domain_name = CONF.openstack.os_user_domain_name
    return keystone_v3_auth.Password(auth_url=auth_url,
                                     username=username,
                                     password=password,
                                     project_name=project_name,
                                     project_domain_name=project_domain_name,
                                     user_domain_name=user_domain_name,
                                     )


def get_keystone_session():
    insecure = CONF.openstack.os_insecure
    if insecure:
        verify = False
    else:
        verify = CONF.openstack.os_cacert

    if CONF.openstack.os_auth_version == '2.0':
        return keystone_session.Session(auth=get_auth_v2(),
                                        verify=verify)
    else:
        return keystone_session.Session(auth=get_auth_v3(),
                                        verify=verify)
