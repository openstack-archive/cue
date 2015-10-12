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

import taskflow.task as task

from cue.common import context as context_module
from cue.db.sqlalchemy import models
from cue import objects


class UpdateClusterStatus(task.Task):

    """this dictionary keeps mapping between valid pass/fail cluster status."""
    status_revert_pairs = {
        models.Status.BUILDING: models.Status.ERROR
    }

    def execute(self, context, cluster_id, cluster_values,
                project_only=True, **kwargs):
        """Main execute method which will update the cluster status in the DB

        :param context: The request context in dict format
        :type context: oslo_context.RequestContext
        :param cluster_id: Unique ID for the cluster
        :type cluster_id: string
        :param cluster_status: Cluster status
        :type cluster_status: string
        """
        request_context = context_module.RequestContext.from_dict(context)
        cluster = objects.Cluster(**cluster_values)
        cluster.update(request_context, cluster_id,
                       project_only=project_only, **kwargs)

    def revert(self, context, cluster_id, cluster_values, **kwargs):
        """Revert UpdateClusterStatus

        This method is executed upon failure of the UpdateClusterStatus or the
        Flow that the Task is part of.  This method will set the cluster status
        to the matching failure status identified by the status_revert_pairs
        mapping.  If a mapping does not exist, the cluster status will be set
        to ERROR.

        :param args: positional arguments that the task required to execute.
        :type args: list
        :param kwargs: keyword arguments that the task required to execute; the
                       special key `result` will contain the :meth:`execute`
                       results (if any) and the special key `flow_failures`
                       will contain any failure information.
        """
        request_context = context_module.RequestContext.from_dict(context)

        if ('status' in cluster_values) and (cluster_values['status']) in (
                UpdateClusterStatus.status_revert_pairs):
            cluster_values['status'] = self.status_revert_pairs[
                cluster_values['status']]
        else:
            cluster_values['status'] = models.Status.ERROR

        cluster = objects.Cluster(**cluster_values)
        cluster.update(request_context, cluster_id)