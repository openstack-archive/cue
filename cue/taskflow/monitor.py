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

import sys
import time

import taskflow.jobs.backends as job_backends
import taskflow.persistence.backends as persistence_backends

PERSISTENCE_BACKEND_CONF = {
    #"connection": "mysql+pymysql://taskflow:taskflow@localhost/taskflow",
    "connection": "zookeeper",
}

JOB_BACKEND_CONF = {
    "board": "zookeeper",
}


def main():
    with persistence_backends.backend(
            PERSISTENCE_BACKEND_CONF.copy()
         ) as persistence:

        with job_backends.backend(
                'tutorial_simple',
                {"board": "zookeeper",
                 "path": "/taskflow/jobs/tutorial_simple"
                },
                persistence=persistence
             ) as board_simple:

            with job_backends.backend(
                    'tutorial_conduct',
                    {"board": "zookeeper",
                     "path": "/taskflow/jobs/tutorial_conduct"
                    },
                    persistence=persistence
                 ) as board_conduct:

                while True:
                    job_count = board_simple.job_count
                    job_count += board_conduct.job_count
                    print("%d outstanding jobs" % (job_count))
                    time.sleep(1)


if __name__ == "__main__":
    sys.exit(main())
