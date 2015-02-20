# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import os_tasklib


class GetVm(os_tasklib.BaseTask):
    """GetVm Task

    This task interfaces with Nova API and retrieves information about a VM

    """

    def execute(self, server):
        """main execute method

        :param server: UUID of the VM to retrieve
        :type server: string
        :return: VM record provided by Nova
        :rtype: dict
        """

        vm_info = self.os_client.servers.get(server=server)
        return vm_info.to_dict()