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

import novaclient.exceptions as nova_exc
from oslo_log import log as logging


LOG = logging.getLogger(__name__)


class DeleteVmGroup(os_tasklib.BaseTask):
    """DeleteVmGroup Task

    This task interfaces with Nova API and deletes a VM server group.

    """

    def execute(self, group):
        """Main execute method

        :param name: ID of the server group to delete
        :type name: string
        :return: n/a
        """
        try:
            self.os_client.server_groups.delete(id=group)
        except nova_exc.NotFound:
            LOG.warning(_LW("Server group was not found %s") % group)
