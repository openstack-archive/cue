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

from cue.common.i18n import _LI  # noqa

from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

MIN_USERNAME_LENGTH = 1
MAX_USERNAME_LENGTH = 255
MIN_PASSWORD_LENGTH = 1
MAX_PASSWORD_LENGTH = 255
PLAIN_AUTH = "PLAIN"


class AuthTokenValidator(object):

    @staticmethod
    def validate_token(auth_type, token):
        auth_validator = None

        if auth_type and auth_type.upper() == PLAIN_AUTH:
            auth_validator = PlainAuthTokenValidator(token=token)
        elif not auth_type:
            return AuthTokenValidator()
        else:
            LOG.info(_LI('Invalid authentication type: %s') % auth_type)

        return auth_validator

    def validate(self):
        return True


class PlainAuthTokenValidator(AuthTokenValidator):
    def __init__(self, token):
        self.token = token

    def validate(self):
        valid_username = False
        valid_password = False

        if self.token:
            if 'username' in self.token:
                if (self.token['username'] and
                    (len(self.token['username']) >= MIN_USERNAME_LENGTH) and
                        (len(self.token['username']) <= MAX_USERNAME_LENGTH)):
                    valid_username = True
                else:
                    LOG.info(_LI('Invalid username: %s')
                              % self.token['username'])

            if 'password' in self.token:
                if (self.token['password'] and
                    (len(self.token['password']) >= MIN_PASSWORD_LENGTH) and
                        (len(self.token['password']) <= MAX_PASSWORD_LENGTH)):
                    valid_password = True
                else:
                    LOG.info(_LI('Invalid password'))

        return valid_username and valid_password
