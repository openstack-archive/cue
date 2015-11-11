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

from cue.common.i18n import _LW  # noqa

from oslo_log import log as logging


LOG = logging.getLogger(__name__)


class CreateVmGroup(os_tasklib.BaseTask):
    """CreateVmGroup Task

    This task interfaces with Nova API and creates a VM group based on
    parameters provided to the Task.

    """

    def execute(self, name, enable_affinity):
        """Main execute method

        :param name: Name of the server group
        :type name: string
        :param enable_affinity:
        :type enable_affinity: Flag to enable affinity or anti-affinity policy
        :rtype: dict
        """
        if enable_affinity:
            policy = "affinity"
        else:
            policy = "anti-affinity"

        new_vm_group = self.os_client.server_groups.create(
            name=name,
            policies=[policy]
        )

        return new_vm_group.to_dict()

    def revert(self, *args, **kwargs):
        """Revert CreateVmGroup Task

        This method is executed upon failure of the CreateVmGroup Task or the
        Flow that the Task is part of.

        :param args: positional arguments that the task required to execute.
        :type args: list
        :param kwargs: keyword arguments that the task required to execute; the
                       special key `result` will contain the :meth:`execute`
                       results (if any) and the special key `flow_failures`
                       will contain any failure information.
        """

        if kwargs.get('tx_id'):
            LOG.warning(_LW("%(tx_id)s Create VM Group failed %(result)s") %
                        {'tx_id': kwargs['tx_id'],
                         'result': kwargs['flow_failures']})
        else:
            LOG.warning(_LW("Create VM Group failed %s") %
                            kwargs['flow_failures'])

        vm_group_info = kwargs.get('result')
        if vm_group_info and isinstance(vm_group_info, dict):
            try:
                vm_group_id = vm_group_info['id']
                if vm_group_id:
                    self.os_client.server_groups.delete(vm_group_id)
            except KeyError:
                pass
