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


class ExceptionTimes(retry.Times):
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

    def __init__(self, revert_exception_list=None, **kwargs):
        super(ExceptionTimes, self).__init__(**kwargs)
        if revert_exception_list:
            self._revert_exception_list = revert_exception_list
        else:
            self._revert_exception_list = []

    def on_failure(self, history, *args, **kwargs):

        (owner, outcome) = history.outcomes_iter(len(history) - 1).next()

        if type(outcome.exception) in self._revert_exception_list:
            return self._revert_action

        return super(ExceptionTimes, self).on_failure(history, args, kwargs)

    def execute(self, history, *args, **kwargs):
        return len(history) + 1
