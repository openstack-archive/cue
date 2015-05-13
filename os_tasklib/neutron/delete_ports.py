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

from cue.common.i18n import _LW  # noqa

import collections

import neutronclient.common.exceptions as neutron_exc
from oslo_log import log as logging
import six

import os_tasklib


LOG = logging.getLogger(__name__)


class DeletePorts(os_tasklib.BaseTask):
    """DeletePort Task

    This task interfaces with Neutron API and creates a port based on the
    parameters provided to the Task.

    """

    def execute(self, port_ids, **kwargs):
        """Main execute method

        :param port_id: Port ID of the port being deleted
        :type port_id: string or list
        """

        if (not isinstance(port_ids, six.string_types) and
            isinstance(port_ids, collections.Iterable)):
            for port_id in port_ids:
                self._delete_port(port_id)

        else:
            self._delete_port(port_ids)

    def _delete_port(self, port_id):
        try:
            self.os_client.delete_port(port=port_id)
        except neutron_exc.NotFound:
            LOG.warning(_LW("Port was not found %s") % port_id)

