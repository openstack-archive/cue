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


__author__ = 'sputnik13'

from os_tasklib import BaseTask
import random


class GetVmStatus(BaseTask):
    def execute(self, vm_id, **kwargs):
        #print self.nova_client.servers.list()
        print "Get VM Status for %s" % vm_id
        vm_status = random.choice(['BUILDING', 'ACTIVE', 'DELETED', 'SUSPENDED', 'PAUSED', 'ERROR', 'STOPPED'])
        return vm_status

    def revert(self, **kwargs):
        print kwargs
