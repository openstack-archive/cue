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

import taskflow.patterns.linear_flow as linear_flow
import taskflow.patterns.unordered_flow as unordered_flow

from cue.db.sqlalchemy import models
from cue.taskflow.flow import check_node_status
import cue.taskflow.task as cue_tasks
import os_tasklib.common as os_common


def check_cluster_status(cluster_id, node_ids):
    """Check Cluster status factory function

    This factory function uses :func:`cue.taskflow.flow.check_node_status` to
    check cluster status on each node.

    :param cluster_id: A unique ID assigned to the cluster being created
    :type cluster_id: string
    :param node_ids: The Cue Node id's associated with each node in the cluster
    :type node_ids: list of uuid strings
    :return: A flow instance that represents the workflow for checking cluster
             status
    """

    flow = linear_flow.Flow("check cluster status %s" % cluster_id)
    sub_flow = unordered_flow.Flow("check status of VMs")

    check_active_status = lambda cluster_status: (ok_status
                                                  if(cluster_status == 'OK')
                                                  else not_ok_status)
    ok_status = {'status': models.Status.ACTIVE}
    not_ok_status = {'status': models.Status.DOWN}

    for i, node_id in enumerate(node_ids):
        sub_flow.add(check_node_status.check_node_status(cluster_id, i,
                                                         node_id))
    flow.add(sub_flow)

    get_cluster_status = os_common.Reduce(
        lambda a, b: a if (a == 'OK') else b,
        provides='cluster_status',
        requires=["%s%d" % ("node_status_", i) for i in range(len(node_ids))]+['node_status_0'],
    )
    flow.add(get_cluster_status)

    translate_cluster_status = os_common.Lambda(
        check_active_status,
        name="translate status to active or down",
        provides="final_cluster_status"
    )
    flow.add(translate_cluster_status)

    update_cluster_status = cue_tasks.UpdateClusterStatus(
        name="update cluster status %s" % cluster_id,
        inject={'cluster_id': cluster_id,
                'project_only': False},
        rebind={'cluster_values': "final_cluster_status"}
    )
    flow.add(update_cluster_status)

    return flow
