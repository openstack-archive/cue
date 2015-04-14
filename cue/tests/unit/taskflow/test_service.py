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

import mock
import signal
import threading

import cue.taskflow.service as tf_service
from cue.tests.unit import base


class TaskflowServiceTest(base.UnitTestCase):
    def setUp(self):
        super(TaskflowServiceTest, self).setUp()

    def tearDown(self):
        super(TaskflowServiceTest, self).tearDown()

    @mock.patch('cue.taskflow.client.create_persistence')
    @mock.patch('cue.taskflow.client.create_jobboard')
    @mock.patch('signal.pause')
    @mock.patch('threading.Thread.start')
    def test_service_thread_launch(self, mock_thread_start, mock_signal_pause,
                                   mock_create_jobboard,
                                   mock_create_persistence):
        assert threading.Thread.start is mock_thread_start
        assert signal.pause is mock_signal_pause
        service = tf_service.ConductorService.create("service_test")
        service.start()
        self.assertTrue(mock_thread_start.called,
                        "Service thread was not started")
        self.assertTrue(mock_signal_pause.called,
                        "signal.pause was not called")
        service.stop()

    @mock.patch('cue.taskflow.client.create_persistence')
    @mock.patch('cue.taskflow.client.create_jobboard')
    @mock.patch('signal.pause')
    @mock.patch('threading.Thread.start')
    def test_create_jobboard_connection(self, mock_thread_start,
                                        mock_signal_pause,
                                        mock_create_jobboard,
                                        mock_create_persistence):
        assert threading.Thread.start is mock_thread_start
        assert signal.pause is mock_signal_pause

        class Closable(object):
            def close(self):
                pass

        mock_create_jobboard.return_value = Closable()
        mock_create_persistence.return_value = Closable()

        service = tf_service.ConductorService.create("service_test")
        service.start()
        self.assertTrue(mock_create_persistence.called,
                        "Persistence was not created")
        self.assertTrue(mock_create_jobboard.called,
                        "Jobboard was not created")
        service.stop()

    @mock.patch('cue.taskflow.client.create_persistence')
    @mock.patch('cue.taskflow.client.create_jobboard')
    @mock.patch('signal.signal')
    def test_set_sighandler(self, mock_signal_signal, mock_create_jobboard,
                            mock_create_persistence):
        assert signal.signal is mock_signal_signal

        # Set signal handler
        service = tf_service.ConductorService.create("service_test")
        service.handle_signals()
        self.assertTrue(mock_signal_signal.called,
                        "Signal handler not called")

    @mock.patch('cue.taskflow.client.create_persistence')
    @mock.patch('cue.taskflow.client.create_jobboard')
    @mock.patch('signal.signal')
    def test_set_sighandler(self, mock_signal_signal, mock_create_jobboard,
                            mock_create_persistence):
        assert signal.signal is mock_signal_signal

        # Set signal handler
        service = tf_service.ConductorService.create("service_test")
        service.handle_signals()
        self.assertTrue(mock_signal_signal.called,
                        "Signal handler not called")
        mock_signal_signal.called = False

        # Change signal handler
        service.handle_signals(signals=[signal.SIGQUIT])
        self.assertTrue(mock_signal_signal.called,
                        "Signal handler not called")

    @mock.patch('cue.taskflow.client.create_persistence')
    @mock.patch('cue.taskflow.client.create_jobboard')
    @mock.patch('signal.signal')
    @mock.patch('signal.pause')
    @mock.patch('threading.Thread.start')
    def test_trigger_sighandler(self, mock_thread_start, mock_signal_pause,
                                mock_signal_signal, mock_create_jobboard,
                                mock_create_persistence):
        assert signal.signal is mock_signal_signal

        # Call sig handler
        service = tf_service.ConductorService.create("service_test")
        service.start()
        service.sighandler(signal.SIGQUIT, None)
        self.assertTrue(mock_signal_signal.called,
                        "Signal handler not called")
        service.stop()

    def test_unsupported_engine(self):
        engine_conf = {'engine': 'worker'}
        self.assertRaises(ValueError, tf_service.ConductorService,
                          engine_conf=engine_conf)