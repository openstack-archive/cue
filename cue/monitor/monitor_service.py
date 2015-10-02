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

import time

from tooz import coordination

from oslo_config import cfg
from oslo_service import loopingcall
from oslo_service import service
import taskflow.patterns.linear_flow as linear_flow
import taskflow.task

from cue.db import api as db_api
from cue.common import policy
import cue.taskflow.client as taskflow_client


class MonitorService(service.Service):

    def __init__(self):
        super(MonitorService, self).__init__()

        zk_url = ("zookeeper://%s:2181"
                  % cfg.CONF.taskflow.zk_hosts)

        self.coordinator = coordination.get_coordinator(zk_url, 'foobar')
        self.coordinator.start()
        # Create a lock
        self.lock = self.coordinator.get_lock("status_check")

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
        pass

    def check(self):
        if not self.lock.acquired:
            self.lock.acquire(blocking=False)

        if self.lock.acquired:

            cluster_ids = get_cluster_ids()

            print "Clusters IDS: \n" + str(cluster_ids) + "\n"

            taskflow_client_instance = taskflow_client.get_client_instance()
            job_list = taskflow_client_instance.joblist()

            for job in job_list:
                if 'cluster_status_check' in job.details['store']:
                    # Nothing to do here
                    print "Debug: Job already exists, not adding it again."
                    return

            print "Adding job..."
            job_args = {
                'cluster_status_check': ''
            }
            taskflow_client_instance.post(create_flow, job_args)

        else:
            print "Debug: Another monitor process has acquired the lock."


class CheckFlow(taskflow.task.Task):
    def execute(self):
        time.sleep(6)


def create_flow():
    return linear_flow.Flow('test flow').add(
        CheckFlow(),
    )


def get_cluster_ids():
    policy.init()

    dbapi = db_api.get_instance()
    clusters = dbapi.get_clusters(None, project_only=False)

    cluster_ids = []
    for cluster in clusters:
        node_ids = []
        for node in dbapi.get_nodes_in_cluster(None, cluster.as_dict()['id']):
            node_ids.append(node.as_dict()['id'])
        cluster_ids.append({cluster.as_dict()['id']: node_ids})

    return cluster_ids
