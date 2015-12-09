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

import time

import taskflow.task as task

from cue.common import exception as cue_exceptions
from cue.db.sqlalchemy import models


class CheckForVmStatus(task.Task):
    def __init__(self,
                 retry_delay_seconds=None,
                 retry_delay_ms=None,
                 name=None,
                 details=None,
                 **kwargs):
        super(CheckForVmStatus, self).__init__(name=name, **kwargs)

        self.sleep_time = 0
        self.details = details
        if retry_delay_seconds:
            self.sleep_time = retry_delay_seconds

        if retry_delay_ms:
            self.sleep_time += retry_delay_ms / 1000.0

    def execute(self, check_var, **kwargs):
        error_string = "expected %s, got %s" % (models.Status.ACTIVE,
                                                check_var)
        if self.details is not None:
            error_string += ", message: %s" % self.details

        if check_var == models.Status.BUILDING:
            raise cue_exceptions.VmBuildingException(error_string)
        elif check_var != models.Status.ACTIVE:
            raise cue_exceptions.VmErrorException(error_string)

    def revert(self, check_var, *args, **kwargs):
        if self.sleep_time != 0:
            time.sleep(self.sleep_time)