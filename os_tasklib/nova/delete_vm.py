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


class DeleteVm(os_tasklib.BaseTask):

    def execute(self, vm_id, **kwargs):
        servers_list = self.os_client.servers.list()
        server_found = False

        for s in servers_list:
            if s.id == vm_id:
                server_found = True
                break

        if server_found:
            self.os_client.servers.delete(s)