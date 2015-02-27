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

import telnetlib as telnet
import time

import taskflow.task


class VerifyNetwork(taskflow.task.Task):
    def __init__(self,
                 retry_delay_seconds=None,
                 retry_delay_ms=None,
                 name=None,
                 **kwargs):
        """Constructor

        This constructor sets the retry delay for this task's revert method.

        :param retry_delay_seconds: retry delay in seconds
        :param retry_delay_ms: retry delay in milliseconds
        :param name: unique name for atom
        """
        super(VerifyNetwork, self).__init__(name=name, **kwargs)

        self.sleep_time = 0
        if retry_delay_seconds:
            self.sleep_time = retry_delay_seconds

        if retry_delay_ms:
            self.sleep_time += retry_delay_ms / 1000.0

    def execute(self, vm_ip, port, **kwargs):
        """Main execute method to verify network connection in a VM

        :param vm_ip: VM ip address
        :type vm_ip: string
        :param port: host service port
        :type port: int
        """
        #tn = telnet.Telnet()
        #tn.open(vm_ip, port, timeout=10)
        pass

    def revert(self, *args, **kwargs):
        """Revert CreateVmTask

        This method is executed upon failure of the GetRabbitVmStatus or the
        Flow that the Task is part of.

        :param args: positional arguments that the task required to execute.
        :type args: list
        :param kwargs: keyword arguments that the task required to execute; the
                       special key `result` will contain the :meth:`execute`
                       results (if any) and the special key `flow_failures`
                       will contain any failure information.
        """
        if self.sleep_time != 0:
            time.sleep(self.sleep_time)
