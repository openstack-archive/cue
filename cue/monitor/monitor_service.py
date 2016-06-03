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

from oslo_config import cfg
from oslo_service import loopingcall
from oslo_service import service
from tooz import coordination

from cue import objects
import cue.taskflow.client as taskflow_client
from cue.taskflow.flow import check_cluster_status


class MonitorService(service.Service):

    def __init__(self):
        super(MonitorService, self).__init__()

        coord_url = ("%s://%s:%s"
                     % (
                         cfg.CONF.taskflow.coord_url,
                         cfg.CONF.taskflow.zk_hosts,
                         cfg.CONF.taskflow.zk_port
                     ))

        self.coordinator = coordination.get_coordinator(
            coord_url, b'cue-monitor')
        self.coordinator.start()
        # Create a lock
        self.lock = self.coordinator.get_lock(b"status_check")

    def start(self):
        loop_interval_seconds = int(cfg.CONF.cue_monitor.loop_interval_seconds)

        pulse = loopingcall.FixedIntervalLoopingCall(
            self.check
        )
        pulse.start(interval=loop_interval_seconds)
        pulse.wait()

    # On stop, try to release the znode
    def stop(self):
        self.lock.release()
        self.coordinator.stop()

    def wait(self):
        pass

    def reset(self):
        self.lock.release()
        self.coordinator.stop()

    def check(self):
        if not self.lock.acquired:
            self.lock.acquire(blocking=False)

        if self.lock.acquired:

            clusters = get_cluster_id_node_ids()

            taskflow_client_instance = taskflow_client.get_client_instance()
            job_list = taskflow_client_instance.joblist()

            cluster_ids = []
            for job in job_list:
                if 'cluster_status_check' in job.details['store']:
                    cluster_ids.append(job.details['store']['cluster_id'])

            filtered_clusters = []
            for cluster in clusters:
                if cluster[0] not in cluster_ids:
                    filtered_clusters.append(cluster)

            for cluster in filtered_clusters:
                job_args = {
                    'cluster_status_check': '',
                    'cluster_id': cluster[0],
                    'context': {},
                    'default_rabbit_user': 'cue_monitor',
                    'default_rabbit_pass': cluster[0],
                }
                flow_kwargs = {
                    'cluster_id': cluster[0],
                    'node_ids': cluster[1]
                }
                taskflow_client_instance.post(check_cluster_status, job_args,
                                              flow_kwargs=flow_kwargs)


# Returns a list of tuples where [0] is cluster_id
# and [1] is a list of that clusters node ids
def get_cluster_id_node_ids():

    clusters = objects.Cluster.get_clusters(None, project_only=False)

    cluster_ids = []
    for cluster in clusters:
        if cluster.status not in ['ACTIVE', 'DOWN']:
            continue
        node_ids = []
        for node in objects.Node.get_nodes_by_cluster_id(None, cluster.id):
            node_ids.append(node.id)
        cluster_ids.append((cluster.id, node_ids))

    return cluster_ids
