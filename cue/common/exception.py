# -*- coding: utf-8 -*-
# Copyright 2014-2015 Hewlett-Packard Development Company, L.P.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
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

"""Cue base exception handling.

Includes decorator for re-raising Cue-type exceptions.

SHOULD include dedicated exception logging.

"""

from oslo_config import cfg
from oslo_log import log as logging
import six

from cue.common.i18n import _  # noqa
from cue.common.i18n import _LE  # noqa


LOG = logging.getLogger(__name__)

exc_log_opts = [
    cfg.BoolOpt('fatal_exception_format_errors',
                default=False,
                help='Make exception message format errors fatal.'),
]

CONF = cfg.CONF
CONF.register_opts(exc_log_opts)


def _cleanse_dict(original):
    """Strip all admin_password, new_pass, rescue_pass keys from a dict."""
    return dict((k, v) for k, v in original.iteritems() if "_pass" not in k)


class CueException(Exception):
    """Base Cue Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:  # pragma: no cover
                pass

        if not message:
            try:
                message = self.message % kwargs

            except Exception as e:
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception(_LE('Exception in string format operation'))
                for name, value in kwargs.iteritems():
                    LOG.error("%s: %s" % (name, value))

                if CONF.fatal_exception_format_errors:
                    raise e
                else:
                    # at least get the core message out if something happened
                    message = self.message

        super(CueException, self).__init__(message)

    def format_message(self):
        if self.__class__.__name__.endswith('_Remote'):
            return self.args[0]
        else:
            return six.text_type(self)


class NotFound(CueException):
    message = _("Not Found")
    code = 404


class NotAuthorized(CueException):
    message = _("Not authorized.")
    code = 403


class OperationNotPermitted(NotAuthorized):
    message = _("Operation not permitted.")


class Invalid(CueException):
    message = _("Unacceptable parameters.")
    code = 400


class Conflict(CueException):
    message = _('Conflict.')
    code = 409


class RequestEntityTooLarge(CueException):
    message = _('Request too large for server.')
    code = 413


class TemporaryFailure(CueException):
    message = _("Resource temporarily unavailable, please retry.")
    code = 503


class InvalidState(Conflict):
    message = _("Invalid resource state.")


class NodeAlreadyExists(Conflict):
    message = _("A node with UUID %(uuid)s already exists.")


class ConfigurationError(CueException):
    message = _("Configuration Error")
