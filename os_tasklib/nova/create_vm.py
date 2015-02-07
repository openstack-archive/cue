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

import os_tasklib


class CreateVm(os_tasklib.BaseTask):
    default_provides = 'nova_vm_id'

    def execute(self, neutron_port_id, cinder_volume_id, **kwargs):
        #print self.os_client.servers.list()
        print("Create VM and attach %s port and %s volume" %
              (neutron_port_id, cinder_volume_id))
        return "RANDOM_VM_ID"

    def revert(self, **kwargs):
        print("Delete VM %s" % kwargs['result'])
