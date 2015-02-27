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

import six
import telnetlib as telnet
import time

import taskflow.task


class CheckOrRestartRabbitMq(taskflow.task.Task):
    """Check or Restart RabbitMQ VM

    This task either checks that RabbitMQ is running or restarts the VM,
    depending on the supplied action.

    """

    def __init__(self,
                 os_client,
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
        super(CheckOrRestartRabbitMq, self).__init__(name=name, **kwargs)

        self.os_client = os_client
        self.sleep_time = 0
        if retry_delay_seconds:
            self.sleep_time = retry_delay_seconds

        if retry_delay_ms:
            self.sleep_time += retry_delay_ms / 1000.0

    def execute(self, action, vm_info, vm_ip, port, **kwargs):
        """main execute method

        :param action: The request context in dict format.
        :type action: oslo_context.RequestContext
        :param vm_info: Unique ID for the node.
        :type vm_info: dict or string
        :param vm_ip:
        :type vm_ip:
        :param port:
        :type port:
        """
        if six.PY2 and isinstance(port, unicode):
            check_port = port.encode()
        else:
            check_port = port

        if isinstance(vm_info, dict):
            vm_id = vm_info['id']
        else:
            vm_id = vm_info

        if action == 'restart':
            self.os_client.servers.reboot(vm_id)
            raise Exception("Restarting VM")

        tn = telnet.Telnet()
        tn.open(vm_ip, check_port, timeout=10)

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
