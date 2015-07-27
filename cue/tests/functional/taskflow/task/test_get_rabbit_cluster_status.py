# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from cue.taskflow.task import get_rabbit_cluster_status
from cue.tests.functional import base
from cue.tests.functional.fixtures import urllib2 as urllib2_fixture

import mock
from taskflow import engines
from taskflow.patterns import linear_flow

import datetime
import urllib2


class GetRabbitClusterStatusTest(base.FunctionalTestCase):
    additional_fixtures = [
        urllib2_fixture.Urllib2Fixture
    ]

    task_store = {
        "vm_ip": "0.0.0.0",
        "default_rabbit_user": "user",
        "default_rabbit_pass": "pass"
    }

    def setUp(self):
        super(GetRabbitClusterStatusTest, self).setUp()

    def test_get_rabbit_cluster_status(self):
        """Verifies GetRabbitClusterStatus task."""

        urllib2_fixture.Urllib2ResultDetails.set_urllib2_result(
            ['{"status": "ok"}',
             '{"status": "clustering"}',
             '[{"name": "/"}]']
        )

        self.flow = linear_flow.Flow(name="wait for RabbitMQ ready state").add(
            get_rabbit_cluster_status.GetRabbitClusterStatus(
                name="get RabbitMQ status",
                retry_delay_seconds=1))

        # start engine
        engines.run(self.flow, store=GetRabbitClusterStatusTest.task_store)

    def test_get_rabbit_cluster_status_fail(self):
        """Verifies unsuccessful path.

        This test simulates when the RMQ vm is not responding to the
        urllib2.open calls on the RMQ management port.
        """
        urllib2_fixture.Urllib2ResultDetails.set_urllib2_result(
            ['{}',
             '[]']
        )

        self.flow = linear_flow.Flow(name="wait for RabbitMQ ready state").add(
            get_rabbit_cluster_status.GetRabbitClusterStatus(
                name="get RabbitMQ status",
                retry_delay_seconds=1))

        # start engine
        engines.run(self.flow, store=GetRabbitClusterStatusTest.task_store)

    @mock.patch('urllib2.build_opener')
    def test_get_rabbit_cluster_status_retry_delay(self, mock_urllib2):
        """Verifies GetRabbitClusterStatus task."""

        mock_urllib2.side_effect = urllib2.URLError("Request denied, yo.")

        urllib2_fixture.Urllib2ResultDetails.set_urllib2_result(
            ['{"status": "ok"}',
             '{"status": "clustering"}',
             '[{"name": "/"}]']
        )

        self.flow = linear_flow.Flow(name="wait for RabbitMQ ready state").add(
            get_rabbit_cluster_status.GetRabbitClusterStatus(
                name="get RabbitMQ status",
                retry_delay_ms=3000))

        start = datetime.datetime.now()
        try:
            # start engine
            engines.run(self.flow, store=GetRabbitClusterStatusTest.task_store)
        except urllib2.URLError:
            # Expected
            pass
        end = datetime.datetime.now()

        # Assert the engine (and revert) took > 5 seconds
        self.assertEqual(True, end - start > datetime.timedelta(seconds=3),
                         "Revert has taken less than 5 seconds, which is"
                         "unexpected when retry_delay_ms is set to 3 seconds")

    @mock.patch('urllib2.build_opener')
    def test_get_rabbit_cluster_status_bad_retry_delay(self, mock_urllib2):
        """Verifies GetRabbitClusterStatus task."""

        mock_urllib2.side_effect = urllib2.URLError("Request denied, yo.")

        urllib2_fixture.Urllib2ResultDetails.set_urllib2_result(
            ['{"status": "ok"}',
             '{"status": "clustering"}',
             '[{"name": "/"}]']
        )

        self.flow = linear_flow.Flow(name="wait for RabbitMQ ready state").add(
            get_rabbit_cluster_status.GetRabbitClusterStatus(
                name="get RabbitMQ status",
                retry_delay_ms=-1))

        start = datetime.datetime.now()
        try:
            # start engine
            engines.run(self.flow, store=GetRabbitClusterStatusTest.task_store)
        except urllib2.URLError:
            # Expected
            pass
        end = datetime.datetime.now()

        # Assert the engine (and revert) took > 5 seconds
        self.assertEqual(True, end - start < datetime.timedelta(seconds=1),
                         "Revert has taken more than 1 second, which is"
                         "unexpected when retry_delay_ms is set to an "
                         "invalid delay time.")