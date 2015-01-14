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
from taskflow.jobs import backends as job_backends
from taskflow.persistence import backends as persistence_backends
from taskflow.conductors import single_threaded

PERSISTENCE_BACKEND_CONF = {
    #"connection": "mysql+pymysql://taskflow:taskflow@localhost/taskflow",
    "connection": "zookeeper",
}

JOB_BACKEND_CONF = {
    "board": "zookeeper",
    "path": "/taskflow/jobs/tutorial_conduct",
}


def main():
    with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) \
            as persistence:

        with job_backends.backend('tutorial_conduct', JOB_BACKEND_CONF.copy(),
                                  persistence=persistence) \
                as board:

            conductor = single_threaded.SingleThreadedConductor(
                "conductor name", board, persistence, engine='serial')

            conductor.run()


if __name__ == "__main__":
    sys.exit(main())
