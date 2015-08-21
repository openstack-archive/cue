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

from cue.common.i18n import _LE  # noqa

from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class AuthTokenValidator(object):

    PLAIN_AUTH = "PLAIN"
    RABBIT_BROKER = "RABBIT"

    @staticmethod
    def validate_token(auth_type, broker_type, token):
        auth_validator = None

        if auth_type and auth_type.upper() == AuthTokenValidator.PLAIN_AUTH:
            if (broker_type and
                    broker_type.upper() == AuthTokenValidator.RABBIT_BROKER):
                auth_validator = RabbitPlainAuthTokenValidator(token=token)
            else:
                LOG.error(_LE('Invalid broker type: %s') % broker_type)
        else:
            LOG.error(_LE('Invalid authentication type: %s') % auth_type)

        return auth_validator

    def validate(self):
        return True


class RabbitPlainAuthTokenValidator(AuthTokenValidator):
    MIN_USERNAME_LENGTH = 1
    MAX_USERNAME_LENGTH = 255
    MIN_PASSWORD_LENGTH = 1
    MAX_PASSWORD_LENGTH = 255

    def __init__(self, token):
        self.token = token

    def validate(self):
        valid_username = False
        valid_password = False

        if self.token is not None:
            if 'username' in self.token:
                if (self.token['username'] and
                    (len(self.token['username']) >=
                        RabbitPlainAuthTokenValidator.MIN_USERNAME_LENGTH) and
                    (len(self.token['username']) <=
                     RabbitPlainAuthTokenValidator.MAX_USERNAME_LENGTH)):
                    valid_username = True
                else:
                    LOG.error(_LE('Invalid username: %s')
                              % self.token['username'])
            if 'password' in self.token:
                if (self.token['password'] and
                    (len(self.token['password']) >=
                        RabbitPlainAuthTokenValidator.MIN_PASSWORD_LENGTH) and
                    (len(self.token['password']) <=
                     RabbitPlainAuthTokenValidator.MAX_PASSWORD_LENGTH)):
                    valid_password = True
                else:
                    LOG.error(_LE('Invalid password: %s')
                              % self.token['password'])

        return valid_username and valid_password
