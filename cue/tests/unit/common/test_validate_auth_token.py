# -*- coding: utf-8 -*-
# Copyright 2014-2015 Hewlett-Packard Development Company, L.P.
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

from cue.common import validate_auth_token as auth_validate
from cue.tests.unit import base


class TestValidateAuthToken(base.UnitTestCase):

    def test_auth_token_validator_base(self):
        validator = auth_validate.AuthTokenValidator()
        valid = validator.validate()
        self.assertEqual(valid, True)

    def test_auth_token_rabbit_validator(self):
        validator = auth_validate.AuthTokenValidator.validate_token(
            auth_type='plain', broker_type='rabbit',
            token={'username': 'rabbitmq',
                   'password': 'rabbit'})
        valid = validator.validate()
        self.assertEqual(valid, True)

    def test_auth_token_invalid_broker(self):
        validator = auth_validate.AuthTokenValidator.validate_token(
            auth_type='plain', broker_type='blah',
            token={'username': 'rabbitmq',
                   'password': 'rabbit'})
        self.assertEqual(validator, None)

    def test_auth_token_invalid_type(self):
        validator = auth_validate.AuthTokenValidator.validate_token(
            auth_type='blah', broker_type='rabbit',
            token={'username': 'rabbitmq',
                   'password': 'rabbit'})
        self.assertEqual(validator, None)

    def test_auth_token_missing_broker(self):
        validator = auth_validate.AuthTokenValidator.validate_token(
            auth_type='plain', broker_type=None,
            token={'username': 'rabbitmq',
                   'password': 'rabbit'})
        self.assertEqual(validator, None)

    def test_auth_token_missing_type(self):
        validator = auth_validate.AuthTokenValidator.validate_token(
            auth_type=None, broker_type='rabbit',
            token={'username': 'rabbitmq',
                   'password': 'rabbit'})
        self.assertEqual(validator, None)

    def test_auth_rabbit_token_missing_username(self):
        validator = auth_validate.AuthTokenValidator.validate_token(
            auth_type='plain', broker_type='rabbit',
            token={'password': 'rabbit'})
        valid = validator.validate()
        self.assertEqual(valid, False)

    def test_auth_rabbit_token_missing_password(self):
        validator = auth_validate.AuthTokenValidator.validate_token(
            auth_type='plain', broker_type='rabbit',
            token={'username': 'rabbitmq'})
        valid = validator.validate()
        self.assertEqual(valid, False)

    def test_auth_rabbit_token_none_username(self):
        validator = auth_validate.AuthTokenValidator.validate_token(
            auth_type='plain', broker_type='rabbit',
            token={'username': None,
                   'password': 'rabbit'})
        valid = validator.validate()
        self.assertEqual(valid, False)

    def test_auth_rabbit_token_none_password(self):
        validator = auth_validate.AuthTokenValidator.validate_token(
            auth_type='plain', broker_type='rabbit',
            token={'username': 'rabbitmq',
                   'password': None})
        valid = validator.validate()
        self.assertEqual(valid, False)

    def test_auth_rabbit_token_invalid_username(self):
        m = (auth_validate.RabbitPlainAuthTokenValidator.MAX_USERNAME_LENGTH
             + 1)
        validator = auth_validate.AuthTokenValidator.validate_token(
            auth_type='plain', broker_type='rabbit',
            token={'username': "x" * m,
                   'password': 'rabbit'})
        valid = validator.validate()
        self.assertEqual(valid, False)

    def test_auth_rabbit_token_invalid_password(self):
        validator = auth_validate.AuthTokenValidator.validate_token(
            auth_type='plain', broker_type='rabbit',
            token={'username': 'rabbitmq',
                   'password': ''})
        valid = validator.validate()
        self.assertEqual(valid, False)