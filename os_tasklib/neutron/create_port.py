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

from oslo_log import log as logging

from cue.common.i18n import _LW  # noqa


LOG = logging.getLogger(__name__)


class CreatePort(os_tasklib.BaseTask):
    """CreatePort Task

    This task interfaces with Neutron API and creates a port based on the
    parameters provided to the Task.

    """
    default_provides = 'neutron_port_id'

    def execute(self, network_id, port_name, security_groups=None, **kwargs):
        """Main execute method

        :param network_id: Network id to connect new port to
        :type network_id: string
        :param port_name: Name for new port
        :type port_name: string
        :param security_groups: Security groups to apply to new port
        :type security_groups: list
        :return: Port record provided by Neutron
        :rtype: dict
        """
        body_value = {
            "port": {
                "admin_state_up": True,
                "name": port_name,
                "network_id": network_id,
            }
        }

        if security_groups:
            body_value['port']['security_groups'] = security_groups

        port = self.os_client.create_port(body=body_value)

        return port

    def revert(self, **kwargs):
        """Revert CreatePort Task

        This method is executed upon failure of the CreatePort Task or the Flow
        that the Task is part of.

        :param args: positional arguments that the task required to execute.
        :type args: list
        :param kwargs: keyword arguments that the task required to execute; the
                       special key `result` will contain the :meth:`execute`
                       results (if any) and the special key `flow_failures`
                       will contain any failure information.
        """
        if kwargs.get('tx_id'):
            LOG.warning(_LW("%(tx_id)s Create Port failed %(result)s") %
                        {'tx_id': kwargs['tx_id'],
                         'result': kwargs['flow_failures']})
        else:
            LOG.warning(_LW("Create Port failed %s") % kwargs['flow_failures'])

        port_info = kwargs.get('result')
        if port_info and isinstance(port_info, dict):
            try:
                port_id = port_info['port']['id']
                if port_id:
                    self.os_client.delete_port(port=port_id)
            except KeyError:
                pass
