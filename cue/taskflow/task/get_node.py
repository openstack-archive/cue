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

from cue.common import context as context_module
from cue import objects

import taskflow.task


class GetNode(taskflow.task.Task):
    """GetNode Task

    This task interfaces with Cue Objects API and retrieves a Node record

    """

    def execute(self, context, node_id, **kwargs):
        """main execute method

        :param context: The request context in dict format.
        :type context: oslo_context.RequestContext
        :param node_id: Unique ID for the node.
        :type node_id: string
        """
        request_context = context_module.RequestContext.from_dict(context)
        node = objects.Node.get_node_by_id(request_context, node_id)
        node_dict = node.as_dict()
        return node_dict