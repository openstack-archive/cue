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

from cue.common import context as context_module
from cue import objects

import taskflow.task


class UpdateNodeRecord(taskflow.task.Task):
    def execute(self, context, node_id, node_values, **kwargs):
        """Main execute method to verify RabbitMQ service in VM

        Once RabbitMQ is verified to be successful, the node's status is
        updated to ACTIVE and respective endpoint is recorded in DB.

        :param context: The request context in dict format.
        :type context: oslo_context.RequestContext
        :param node_id: Unique ID for the node.
        :type node_id: string
        :param node_values: New node values for updating record
        :type node_values: dict
        """
        request_context = context_module.RequestContext.from_dict(context)
        node = objects.Node(**node_values)
        node.update(request_context, node_id)