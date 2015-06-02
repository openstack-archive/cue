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


LOG = logging.getLogger(__name__)


_INTERFACE_ATTRIBUTES = [
    'fixed_ips',
    'mac_addr',
    'net_id',
    'port_id',
    'port_state'
]


class ListVmInterfaces(os_tasklib.BaseTask):
    """ListVmInterfaces Task

    This task interfaces with Nova API and retrieves the list of interfaces
    attached to the indicated VM.

    """
    def execute(self, server, **kwargs):
        """Main execute method

        :param server: vm id to get list of attached interfaces to
        :type server: string
        :return: list of interfaces
        """
        raw_list = self.os_client.servers.interface_list(server=server)

        # The interface returned by Nova API has circular references which
        # break serialization of the list to storage, so a subset of the data
        # is being extracted and returned.

        interface_list = list()
        for interface in raw_list:
            interface_entry = {k: getattr(interface, k)
                               for k in _INTERFACE_ATTRIBUTES
                               if hasattr(interface, k)}
            interface_list.append(interface_entry)

        return interface_list
