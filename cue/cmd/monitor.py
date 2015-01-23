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

import sys
import time

import oslo.config.cfg as cfg
from oslo_log import log
import taskflow.jobs.backends as job_backends
import taskflow.persistence.backends as persistence_backends

import cue.common.service as cue_service

PERSISTENCE_BACKEND_CONF = {
    "connection": "zookeeper",
    "hosts": "localhost",
    "path": "/cue/taskflow",
}

JOB_BACKEND_CONF = {
    "board": "zookeeper",
    "path": "/cue/taskflow/jobs",
}

CONF = cfg.CONF


def main():
    cue_service.prepare_service(sys.argv)

    LOG = log.getLogger(__name__)

    with persistence_backends.backend(
            PERSISTENCE_BACKEND_CONF.copy()
         ) as persistence:

        with job_backends.backend(
                'tutorial_simple',
                JOB_BACKEND_CONF.copy(),
                persistence=persistence
             ) as board:

                while True:
                    job_count = board.job_count
                    LOG.info("%d outstanding jobs" % (job_count))
                    time.sleep(1)


if __name__ == "__main__":
    sys.exit(main())
