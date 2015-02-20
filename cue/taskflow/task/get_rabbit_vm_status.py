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

from cue.common import context as context_module
from cue.db.sqlalchemy import models
from cue import objects

import base_task as base_task


class GetRabbitVmStatus(base_task.BaseTask):
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
        super(GetRabbitVmStatus, self).__init__(name=name, **kwargs)

        self.sleep_time = 0
        if retry_delay_seconds:
            self.sleep_time = retry_delay_seconds

        if retry_delay_ms:
            self.sleep_time += retry_delay_ms / 1000.0

    def execute(self, context, node_id, vm_ip, rabbit_port, **kwargs):
        """Main execute method to verify RabbitMQ service in VM

        Once RabbitMQ is verified to be successful, the node's status is
        updated to ACTIVE.

        :param context: The request context in dict format.
        :type context: oslo_context.RequestContext
        :param node_id: Unique ID for the node.
        :type node_id: string
        :param vm_ip: VM ip address where rabbitMQ is running
        :type vm_ip: string
        :param rabbit_port: RabbitMQ AMQP interface port
        :type rabbit_port: int
        """
        tn = telnet.Telnet()
        tn.open(vm_ip, rabbit_port, timeout=10)
        if 'user_identity' in context:
            del context['user_identity']
        request_context = context_module.RequestContext(**context)
        objects.Node.update_node_status(request_context, node_id,
                                        models.Status.ACTIVE)

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
