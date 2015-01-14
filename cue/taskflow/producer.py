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

__author__ = 'sputnik13'

from taskflow.jobs import backends as job_backends
from oslo.utils import uuidutils
from taskflow.persistence import backends as persistence_backends
from taskflow.persistence import logbook
from taskflow import engines

from time import sleep
import sys

import cue.taskflow.flow.create_cluster as create_cluster

PERSISTENCE_BACKEND_CONF = {
    #"connection": "mysql+pymysql://taskflow:taskflow@localhost/taskflow",
    "connection": "zookeeper",
}

JOB_BACKEND_CONF = {
    "board": "zookeeper",
    "path": "/taskflow/jobs/tutorial_conduct",
}


def main():
    count = 1
    with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) \
            as persistence:

        with job_backends.backend('tutorial_conduct', JOB_BACKEND_CONF.copy(),
                                  persistence=persistence) \
                as board:

            while True:
                print "test loop %d" % (count)
                job_name = "Job #%d" % (count)
                job_logbook = logbook.LogBook(job_name)
                flow_detail = logbook.FlowDetail(job_name,
                                                 uuidutils.generate_uuid())
                factory_args = ()
                factory_kwargs = {}
                engines.save_factory_details(flow_detail, create_cluster,
                                             factory_args, factory_kwargs)
                job_logbook.add(flow_detail)
                persistence.get_connection().save_logbook(job_logbook)
                job_details = {
                    'store': {
                    }
                }
                job = board.post(job_name,
                                 book=job_logbook,
                                 details=job_details)
                print "%s posted" % (job)
                sleep(1)
                count += 1

if __name__ == "__main__":
    sys.exit(main())
