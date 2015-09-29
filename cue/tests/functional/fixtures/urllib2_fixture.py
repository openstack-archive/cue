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

import StringIO

from six.moves import urllib

import cue.tests.functional.fixtures.base as base


class Urllib2ResultDetails(object):
    urllib2_result_list = []

    @staticmethod
    def set_urllib2_result(results):
        """Helper function to setup sequence of fixed results.

        :param results: list of results
        """
        for result in results:
            io = StringIO.StringIO(result)
            Urllib2ResultDetails.urllib2_result_list.append(io)

    @staticmethod
    def get_urllib2_result():
        """Returns the next result in configured sequence.

        If result sequence is empty, an empty string result of '' is returned.

        :return: Current urllib result in urllib2_result_list.
        """
        if len(Urllib2ResultDetails.urllib2_result_list) == 0:
            result = ''
        else:
            result = Urllib2ResultDetails.urllib2_result_list.pop()
        return result


class Urllib2Fixture(base.BaseFixture):
    """A test fixture to simulate urllib2 calls

    This class is used in test cases to simulate urllib2 calls.
    """
    def __init__(self, *args, **kwargs):
        super(Urllib2Fixture, self).__init__(*args, **kwargs)

    def setUp(self):
        """Set up test fixture and apply all method overrides."""
        super(Urllib2Fixture, self).setUp()

        urllib2_client = self.mock('six.moves.urllib.request.OpenerDirector')
        urllib2_client.open = self.open

    def open(self, url):
        result = Urllib2ResultDetails.get_urllib2_result()
        if result.getvalue() is 'URLError':
            raise urllib.error.URLError('urlerror')
        return result
