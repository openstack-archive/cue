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

import os

from oslo_config import cfg

TEST_CONF = None


def setup_config(config_file=''):
    global TEST_CONF
    TEST_CONF = cfg.ConfigOpts()

    identity_group = cfg.OptGroup(name='identity')
    identity_options = [
        cfg.StrOpt('auth_version', default='3'),
        cfg.StrOpt('uri', default='http://localhost:5000/v3'),
        cfg.StrOpt('username', default='demo'),
        cfg.StrOpt('password', default='password'),
        cfg.StrOpt('tenant_name', default='demo'),
        cfg.StrOpt('project_name', default='demo'),
        cfg.StrOpt('user_domain_name', default='default'),
        cfg.StrOpt('project_domain_name', default='default')
    ]
    TEST_CONF.register_group(identity_group)
    TEST_CONF.register_opts(identity_options, group=identity_group)

    message_broker_group = cfg.OptGroup(name='message_broker')
    message_broker_options = [
        cfg.StrOpt('flavor', default='8795'),
    ]
    TEST_CONF.register_group(message_broker_group)
    TEST_CONF.register_opts(message_broker_options, group=message_broker_group)

    # Figure out which config to load
    config_to_load = []
    local_config = 'cue-integration.conf'
    if os.path.isfile(config_file):
        config_to_load.append(config_file)
    elif os.path.isfile(local_config):
        config_to_load.append(local_config)
    else:
        config_to_load.append('/etc/cue/cue-integration.conf')

    # Actually parse config
    TEST_CONF(
        (),  # Required to load a anonymous config
        default_config_files=config_to_load
    )


def get_config():
    if not TEST_CONF:
        setup_config()
    return TEST_CONF
