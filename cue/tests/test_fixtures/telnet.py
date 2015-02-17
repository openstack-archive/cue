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

import telnetlib as telnet

import cue.tests.test_fixtures.base as base


class TelnetStatusDetails(object):
    telnet_status_list = []

    @staticmethod
    def set_vm_status(statuses):
        """Helper function to setup sequence of status labels.

        :param statuses: list of statuses
        """
        for status in statuses:
            TelnetStatusDetails.telnet_status_list.append(status)

    @staticmethod
    def get_status():
        """Returns the next status in configured sequence.

        If status sequence is empty, a status of 'ready' is returned.

        :return: Current RabbitMQ VM status.
        """
        if len(TelnetStatusDetails.vm_status_list) == 0:
            status = 'ready'
        else:
            status = TelnetStatusDetails.telnet_status_list.pop()

        return status


class TelnetClient(base.BaseFixture):
    """A test fixture to simulate a Telnet connection

    This class is used in test cases to simulate a telnet client connection.
    """

    def __init__(self, *args, **kwargs):
        super(TelnetClient, self).__init__(*args, **kwargs)

    def setUp(self):
        """Set up test fixture and apply all method overrides."""
        super(TelnetClient, self).setUp()

        self.mock(telnet.Telnet)
        #telnet_client.__init__ = TelnetStatusDetails.get_status
        