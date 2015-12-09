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

import taskflow.retry as retry
from taskflow.utils import misc
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class ErroredTimes(retry.Times):
    """Retries subflow given number of times. Returns attempt number.
    :param attempts: number of attempts to retry the associated subflow
                     before giving up
    :type attempts: int
    :param revert_all: when provided this will cause the full flow to revert
                       when the number of attempts that have been tried
                       has been reached (when false, it will only locally
                       revert the associated subflow)
    :type revert_all: bool
    Further arguments are interpreted as defined in the
    :py:class:`~taskflow.atom.Atom` constructor.
    """

    def __init__(self, attempts=1, name=None, provides=None, requires=None,
                 auto_extract=True, rebind=None, revert_all=False):
        super(retry.Times, self).__init__(name, provides, requires,
                                    auto_extract, rebind)
        self._attempts = attempts

        if revert_all:
            self._revert_action = retry.REVERT_ALL
        else:
            self._revert_action = retry.REVERT

    def on_failure(self, history, *args, **kwargs):

        failures = list(history.outcomes_iter())
        error_details = []
        for owner,outcome in failures:
            error_details.append(str(outcome))

        error_msg = error_details[len(error_details)-1]

        current_status = error_msg.split('AssertionError')[1]
        if 'ERROR' in current_status:
            return self._revert_action

        elif len(history) < self._attempts:
            return retry.RETRY
        else:
            return self._revert_action

    def execute(self, history, *args, **kwargs):
        return len(history) + 1