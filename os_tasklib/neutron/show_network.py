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


class ShowNetwork(os_tasklib.BaseTask):
    """ShowNetwork Task

    This task interfaces with Neutron API and retrieves information about the
    specified network.

    """

    def execute(self, network, **kwargs):
        """Main execute method

        :param network_id: Network id to connect new port to
        :type network_id: string
        :return: Port record provided by Neutron
        :rtype: dict
        """
        network = self.os_client.show_network(network=network)

        return network['network']
