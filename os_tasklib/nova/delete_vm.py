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

from cue.common.i18n import _LI  # noqa

from oslo_log import log as logging


LOG = logging.getLogger(__name__)


class DeleteVm(os_tasklib.BaseTask):
    """DeleteVm Task

    This task interfaces with Nova API and deletes a VM identified by the
    VM ID provided to the Task.

    """
    def execute(self, vm_id, **kwargs):
        """Main execute method

        :param vm_id: Network id to connect new port to
        :type vm_id: string
        :return: n/a
        """
        self.os_client.servers.delete(vm_id)
        LOG.info(_LI('Deleting VM, id: %s') % vm_id)
