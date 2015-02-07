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


class CreatePort(os_tasklib.BaseTask):
    default_provides = 'neutron_port_id'

    def execute(self, network_id, **kwargs):
        body_value = {
            "port": {
                "admin_state_up": True,
                "name": 'cue_port',
                "network_id": network_id,
            }
        }

        port = self.os_client.create_port(body=body_value)
        port_id = port['port']['id']

        return port_id

    def revert(self, **kwargs):
        """Revert function for a failed create port task."""
        # TODO(dagnello): no action required for revert of a failed port create
        # task, but logging should be added with a flow transaction ID which
        # will provide context and state to the error.
