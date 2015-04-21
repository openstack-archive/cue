# Copyright 2014, Hewlett-Packard
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
from oslo_config import fixture

from cue.common import exception
from cue.common.i18n import _  # noqa
from cue.tests.unit import base


class MissingKwargException(exception.CueException):
    message = _("%s %s")

class Exception_Remote(exception.CueException):
    message = _("Remote Error")

class TestCommonException(base.UnitTestCase):

    def test_valid_exception(self):
        e = exception.NotFound()
        e.format_message()

    def test_coded_exception(self):
        e = exception.CueException(code=1)
        self.assertEqual(1, e.kwargs['code'])

    @mock.patch('logging.LoggerAdapter.exception')
    @mock.patch('logging.LoggerAdapter.error')
    def test_missing_kwarg_exception(self, mock_log_error, mock_log_exception):
        e = MissingKwargException()
        self.assertEqual(True, mock_log_error.called)
        self.assertEqual(True, mock_log_exception.called)

    @mock.patch('logging.LoggerAdapter.exception')
    @mock.patch('logging.LoggerAdapter.error')
    def test_exception_on_format_error(self,
                                       mock_log_error,
                                       mock_log_exception):
        e = MissingKwargException()
        self.assertEqual(True, mock_log_error.called)
        self.assertEqual(True, mock_log_exception.called)

    def test_cleanse_dict(self):
        d = {
            'admin_pass': 'admin_pass',
            'new_pass': 'new_pass',
            'rescue_password': 'rescue_password',
            'test_key': 'test_value',
        }

        clean_d = exception._cleanse_dict(d)
        expected = {'test_key': 'test_value'}
        self.assertDictEqual(expected, clean_d)

    def test_remote_exception(self):
        e = Exception_Remote()
        msg = e.format_message()
        self.assertEqual(_("Remote Error"), msg)
