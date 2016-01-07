# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
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

import mock

from cue.common import exception
from cue.common.i18n import _  # noqa
from cue.tests.functional import base


class MissingKwargException(exception.CueException):
    message = _("%s %s")  # noqa


class TestCommonException(base.FunctionalTestCase):
    @mock.patch('logging.LoggerAdapter.exception')
    @mock.patch('logging.LoggerAdapter.error')
    def test_exception_on_format_error(self,
                                       mock_log_error,
                                       mock_log_exception):
        self.CONF.config(fatal_exception_format_errors=True)
        self.assertRaises(TypeError, MissingKwargException)
        self.assertTrue(mock_log_error.called)
        self.assertTrue(mock_log_exception.called)
