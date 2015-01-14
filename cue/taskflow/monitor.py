# -*- coding: utf-8 -*-

__author__ = 'sputnik13'

from taskflow.jobs import backends as job_backends
from taskflow.persistence import backends as persistence_backends

from time import sleep
import sys

PERSISTENCE_BACKEND_CONF = {
    #"connection": "mysql+pymysql://taskflow:taskflow@localhost/taskflow",
    "connection": "zookeeper",
}

JOB_BACKEND_CONF = {
    "board": "zookeeper",
}


def main():
    with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) \
            as persistence:

        with job_backends.backend('tutorial_simple',
                                  {"board": "zookeeper",
                                   "path": "/taskflow/jobs/tutorial_simple"},
                                  persistence=persistence) \
                as board_simple:

            with job_backends.backend('tutorial_conduct',
                                      {"board": "zookeeper",
                                       "path": "/taskflow/jobs/tutorial_conduct"},
                                      persistence=persistence) \
                    as board_conduct:

                while True:
                    job_count = board_simple.job_count
                    job_count += board_conduct.job_count
                    print "%d outstanding jobs" % (job_count)
                    sleep(1)


if __name__ == "__main__":
    sys.exit(main())
