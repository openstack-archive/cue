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

from cue.common.i18n import _LW  # noqa
from cue.openstack.common import log as logging

LOG = logging.getLogger(__name__)

import base_task as base_task


class GetRabbitVmStatus(base_task.BaseTask):
    def execute(self, vm_ip, rabbit_port, **kwargs):
        """Main execute method

        :param vm_ip: VM ip address where rabbitMQ is running
        :type rabbit_port: RabbitMQ AMQP interface port
        :return: 'ready' status if telnet connection to port is successful
        """
        telnet.Telnet(vm_ip, rabbit_port)
        return 'ready'

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

        if kwargs.get('tx_id'):
            LOG.warning(_LW("%(tx_id)s Get Rabbit VM Status failed %(result)s")
                        % {'tx_id': kwargs['tx_id'],
                           'result': kwargs['flow_failures']})
        else:
            LOG.warning(_LW("Get Rabbit VM Status Failed %s") %
                        kwargs['flow_failures'])
