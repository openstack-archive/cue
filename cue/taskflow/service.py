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
import contextlib
import logging as std_logging
import time

import eventlet.event as event
from oslo.config import cfg
from oslo_log import log as logging
from taskflow.conductors import single_threaded

import cue.openstack.common.service as os_service
import cue.taskflow.client as tf_client
import cue.version as version


LOG = logging.getLogger(__name__)

CONF = cfg.CONF

SUPPORTED_ENGINE_TYPES = ['serial', 'parallel']


class ConductorService(os_service.Service):
    """A Service wrapper for executing taskflow jobs in a conductor.

    This class provides an oslo.service.Service wrapper for executing taskflow
    jobs in a conductor.

    This wrapper is compatible with both single process and multi-process
    launchers.
    """
    def __init__(self, host=None, jobboard_name=None, jobboard_conf=None,
                 persistence_conf=None, engine_conf=None, wait_timeout=None,
                 *args, **kwargs):
        """Constructor for ConductorService

        :param host: Name to be used to identify the host running the conductor
        :param jobboard_name: Name of the jobboard
        :param jobboard_conf: Configuration parameters for the jobboard
                              backend.  This configuration is passed forward to
                              :meth:`cue.taskflow.client.Client.jobboard`.
        :param persistence_conf: Configuration parameters for the persistence
                                 backend.  This configuration is passed forward
                                 to
                                 :meth:`cue.taskflow.client.Client.persistence`
        :param engine_conf: A dictionary containing onfiguration parameters for
                            the engine used by the conductor.  The 'engine'
                            parameter specifies the engine type.  Currently
                            only 'serial' and 'parallel' engine types are
                            supported.
        :param wait_timeout: The number of seconds to wait for a new job to
                             appear when waiting for jobs.
        :param args: Positional arguments to be passed to the jobboard and
                     persistence backend constructors
        :param kwargs: Keyword arguemtns to be passed to the jobboard and
                       persistence backend constructors
        """
        super(ConductorService, self).__init__(*args, **kwargs)

        if (engine_conf['engine'] not in SUPPORTED_ENGINE_TYPES):
            raise ValueError("%s is not a supported engine type"
                             % engine_conf['engine'])

        self._host = host

        self._jobboard_name = jobboard_name
        self._jobboard_conf = jobboard_conf
        self._persistence_conf = persistence_conf
        self._engine_conf = engine_conf
        self._wait_timeout = wait_timeout
        self._shutdown_event = event.Event()
        self._args = args
        self._kwargs = kwargs

    @classmethod
    def create(cls, host=None, jobboard_name=None, jobboard_conf=None,
               persistence_conf=None, engine_conf=None, wait_timeout=1,
               *args, **kwargs):
        """Factory method for creating a ConductorService instance

        :param host: Name to be used to identify the host running the conductor
        :param jobboard_name: Name of the jobboard
        :param jobboard_conf: Configuration parameters for the jobboard
                              backend.  This configuration is passed forward to
                              :meth:`cue.taskflow.client.Client.jobboard`.
        :param persistence_conf: Configuration parameters for the persistence
                                 backend.  This configuration is passed forward
                                 to
                                 :meth:`cue.taskflow.client.Client.persistence`
        :param engine_conf: A dictionary containing onfiguration parameters for
                            the engine used by the conductor.  The 'engine'
                            parameter specifies the engine type.  Currently
                            only 'serial' and 'parallel' engine types are
                            supported.
        :param wait_timeout: The number of seconds to wait for a new job to
                             appear when waiting for jobs.
        :param args: Positional arguments to be passed to the jobboard and
                     persistence backend constructors
        :param kwargs: Keyword arguments to be passed to the jobboard and
                       persistence backend constructors
        :return: A :class:`.ConductorService` instance.
        """
        engine_conf = engine_conf or {}
        engine_conf.setdefault('engine', CONF.taskflow.engine_type)

        return cls(host, jobboard_name, jobboard_conf, persistence_conf,
                   engine_conf, wait_timeout, *args, **kwargs)

    def start(self):
        """Interface to start the ConductorService."""
        super(ConductorService, self).start()

        CONF.log_opt_values(LOG, std_logging.INFO)

        version_string = version.version_info.version_string()
        LOG.debug("Starting runner %s on board %s",
                  version_string, self._jobboard_name)

        with contextlib.closing(
                tf_client.Client.persistence(conf=self._persistence_conf)
        ) as persistence:
            with contextlib.closing(
                    tf_client.Client.jobboard(
                        board_name=self._jobboard_name,
                        conf=self._jobboard_conf,
                        persistence=persistence,
                    )
            ) as jobboard:
                self._conductor = single_threaded.SingleThreadedConductor(
                    name=self._host,
                    jobboard=jobboard,
                    persistence=persistence,
                    engine=self._engine_conf['engine'],
                    wait_timeout=self._wait_timeout)

                time.sleep(0.5)
                self._conductor.run()

        self._shutdown_event.send()

    def stop(self):
        """Interface to stop the ConductorService."""
        self._shutdown = True
        self._conductor.stop()
        super(ConductorService, self).stop()

    def wait(self):
        """Interface to wait for ConductorService to complete."""
        self._shutdown_event.wait()
        super(ConductorService, self).wait()
