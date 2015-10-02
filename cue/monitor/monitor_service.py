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

from oslo_service import loopingcall
from oslo_service import service
import taskflow.patterns.linear_flow as linear_flow
import taskflow.task

from cue.common import context as cue_context
from cue.common import policy
from cue import objects
import cue.taskflow.client as tf_client


class MonitorService(service.Service):

    def __init__(self):
        super(MonitorService, self).__init__()

        #TODO (dan) May want to go grab zk_url from cue.conf
        zk_url = 'zookeeper://127.0.0.1:2181'

        self.coordinator = coordination.get_coordinator(zk_url, 'foobar')
        self.coordinator.start()
        # Create a lock
        self.lock = self.coordinator.get_lock("status_check")

    def start(self):
        # May want to put this in cue.conf?
        loop_interval = 5

        pulse = loopingcall.FixedIntervalLoopingCall(
            self.check
        )
        pulse.start(interval=loop_interval)
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

            # get_cluster_ids()

            tf_client_instance = tf_client.get_client_instance()
            job_list = tf_client_instance.joblist()

            for job in job_list:
                if 'cluster_status_check' in job.details['store']:
                    # Nothing to do here
                    return

            print "Adding job..."
            job_args = {
                'cluster_status_check': ''
            }
            tf_client_instance.post(create_flow, job_args)

        else:
            print "Another monitor process has acquired the lock."


class CheckFlow(taskflow.task.Task):
    def execute(self):
        time.sleep(6)


def create_flow():
    return linear_flow.Flow('test flow').add(
        CheckFlow(),
    )


def get_context():
    # auth_token = kwargs.get('auth_token', "auth_xxx")
    # user = kwargs.get("user", "user")
    # tenant = kwargs.get("tenant", "tenant-a")
    return cue_context.RequestContext(auth_token="auth_xxx",
                                      user='cue',
                                      tenant='admin',
                                      )


def get_cluster_ids():
    policy.init()
    context = get_context()
    clusters = objects.Cluster.get_clusters(context)
    print "Clusters: "
    for cluster in clusters:
        print " -  " + str(cluster)

