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

import os_tasklib


class GetVmStatus(os_tasklib.BaseTask):
    """GetVmStatus Task

    This task will retrieve the current status of the indicated VM

    """
    def execute(self, vm_id, **kwargs):
        """Main execute method

        :param vm_id: VM id to get status of
        :type param: string
        :return: VM status
        :rtype: string
        """
        server = self.os_client.servers.get(vm_id)
        return server.status

    def revert(self, **kwargs):
        print(kwargs)
