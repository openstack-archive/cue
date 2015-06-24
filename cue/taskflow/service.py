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

import signal
import threading
import time

from oslo_config import cfg
from oslo_log import log as logging
from taskflow.conductors import single_threaded

import cue.taskflow.client as tf_client
import cue.version as version


LOG = logging.getLogger(__name__)

CONF = cfg.CONF

SUPPORTED_ENGINE_TYPES = ['serial', 'parallel']


class ConductorService(object):
    """A Service wrapper for executing taskflow jobs in a conductor.

    This class provides an oslo.service.Service wrapper for executing taskflow
    jobs in a conductor.

    This wrapper is compatible with both single process and multi-process
    launchers.
    """
    def __init__(self, host=None, jobboard=None, jobboard_name=None,
                 jobboard_conf=None, persistence=None, persistence_conf=None,
                 engine_conf=None, wait_timeout=None, *args, **kwargs):
        """Constructor for ConductorService

        :param host: Name to be used to identify the host running the conductor
        :param jobboard: Jobboard instance to be used by conductor service
        :param jobboard_name: Name of the jobboard
        :param jobboard_conf: Configuration parameters for the jobboard
                              backend.  This configuration is passed forward to
                              :meth:`cue.taskflow.client.Client.jobboard`.
        :param persistence: Persistence instance to be used by conductor
                            service
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
        if (engine_conf['engine'] not in SUPPORTED_ENGINE_TYPES):
            raise ValueError("%s is not a supported engine type"
                             % engine_conf['engine'])

        self._host = host

        self._jobboard = jobboard
        self._jobboard_name = jobboard_name
        self._jobboard_conf = jobboard_conf
        self._persistence = persistence
        self._persistence_conf = persistence_conf
        self._engine_conf = engine_conf
        self._wait_timeout = wait_timeout
        self._shutdown_event = threading.Event()
        self._args = args
        self._kwargs = kwargs

        self._signal_list = None

    @classmethod
    def create(cls, host=None, jobboard=None, jobboard_name=None,
               jobboard_conf=None, persistence=None, persistence_conf=None,
               engine_conf=None, wait_timeout=1, *args, **kwargs):
        """Factory method for creating a ConductorService instance

        :param host: Name to be used to identify the host running the conductor
        :param jobboard: Jobboard instance to be used by conductor service
        :param jobboard_name: Name of the jobboard
        :param jobboard_conf: Configuration parameters for the jobboard
                              backend.  This configuration is passed forward to
                              :meth:`cue.taskflow.client.Client.jobboard`.
        :param persistence: Persistence instance to be used by conductor
                            service
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

        return cls(host, jobboard, jobboard_name, jobboard_conf, persistence,
                   persistence_conf, engine_conf, wait_timeout, *args,
                   **kwargs)

    def start(self):
        """Interface to start the ConductorService."""
        version_string = version.version_info.version_string()
        LOG.debug("Starting runner %s on board %s",
                  version_string, self._jobboard_name)

        persistence = self._persistence
        jobboard = self._jobboard
        try:
            # Create persistence and/or jobboard if they weren't passed in
            if persistence is None:
                persistence = tf_client.create_persistence(
                    conf=self._persistence_conf)

            if jobboard is None:
                jobboard = tf_client.create_jobboard(
                    board_name=self._jobboard_name,
                    conf=self._jobboard_conf,
                    persistence=persistence,
                )

            self._conductor = single_threaded.SingleThreadedConductor(
                name=self._host,
                jobboard=jobboard,
                persistence=persistence,
                engine=self._engine_conf['engine'],
                wait_timeout=self._wait_timeout)

            time.sleep(0.5)
            if threading.current_thread().name == 'MainThread':
                t = threading.Thread(target=self._conductor.run)
                t.start()
                signal.pause()
            else:
                self._conductor.run()

        finally:
            # Close persistence and jobboard if they were created by us
            if self._persistence is None:
                persistence.close()

            if self._jobboard is None:
                jobboard.close()

        self._shutdown_event.set()

    def stop(self):
        """Interface to stop the ConductorService."""
        self._conductor.stop()

    def wait(self):
        """Interface to wait for ConductorService to complete."""
        self._shutdown_event.wait()

    def handle_signals(self, signals=None, handler=None):
        """Set signal handlers

        Set OS signal handlers.  By default SIGHUP, SIGINT, and SIGTERM are
        handled.
        """

        if signals is None:
            signals = [
                signal.SIGHUP,
                signal.SIGINT,
                signal.SIGTERM,
            ]

        if self._signal_list is None:
            self._signal_list = signals

        if cmp(signals, self._signal_list):
            for s in set(self._signal_list):
                signal.signal(s, signal.SIG_DFL)

        if handler is None:
            handler = self.sighandler

        for s in set(signals):
            signal.signal(s, handler)

    def sighandler(self, signum, frame):
        self.handle_signals(signals=self._signal_list, handler=signal.SIG_DFL)
        self.stop()
