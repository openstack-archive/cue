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
    status_revert_pairs = {
        models.Status.BUILDING: models.Status.ERROR
    }

    def execute(self, context, cluster_id, cluster_status, **kwargs):
        if 'user_identity' in context:
            del context['user_identity']
        request_context = context_module.RequestContext(**context)
        objects.Cluster.update_cluster_status(request_context, cluster_id,
                                              cluster_status)

    def revert(self, *args, **kwargs):
        if 'user_identity' in kwargs['context']:
            del kwargs['context']['user_identity']
        request_context = context_module.RequestContext(**kwargs['context'])
        cluster_id = kwargs['cluster_id']
        if kwargs['cluster_status'] in UpdateClusterStatus.status_revert_pairs:
            objects.Cluster.update_cluster_status(
                request_context, cluster_id,
                UpdateClusterStatus.status_revert_pairs
                [kwargs['cluster_status']])
        else:
            objects.Cluster.update_cluster_status(request_context, cluster_id,
                                                  models.Status.ERROR)