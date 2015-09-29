# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import contextlib
import sys

import mock
import six

from cue.common import exception
from cue.manage import broker as cue_manage
from cue.objects import broker
from cue.objects import broker_metadata
from cue.tests.unit import base as test_base


@contextlib.contextmanager
def stdout_redirect(where):
    sys.stdout = where
    try:
        yield where
    finally:
        sys.stdout = sys.__stdout__


class FakeBroker():
    def __init__(self, id, name, active, created_at, updated_at,
                 deleted_at):
        self.id = id
        self.name = name
        self.active = active
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at


class FakeBrokerMetadata():
    def __init__(self, id, broker_id, key, value, created_at,
                 updated_at, deleted_at):
        self.id = id
        self.broker_id = broker_id
        self.key = key
        self.value = value
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at


class TestBroker(test_base.UnitTestCase):

    cue_manage_broker = None

    def setUp(self):
        super(TestBroker, self).setUp()

        self.cue_manage_broker = cue_manage.BrokerCommands()

    @mock.patch('cue.objects.broker.Broker.create_broker')
    def test_broker_add(self, mock_add_broker):
        """Test 'cue-manage broker add'

        Mocks the cue/objects/broker.py create_broker() function and asserts
        that it received the context from cue-manage
        """

        broker_name = "test_broker"
        active_status = "True"
        self.cue_manage_broker.add(broker_name, active_status)

        mock_add_broker.assert_called_once_with(self.cue_manage_broker.context)

    def test_broker_add_check_result(self):
        """Test 'cue-manage broker add' return value

        Mocks the cue/objects/broker.py create_broker() call to return a fake
        broker object with specific attributes and asserts that broker object
        is printed to std_out
        """
        broker_name = "test_broker"
        active_status = "True"

        fake_broker = FakeBroker('test_id', broker_name, active_status,
                                 'test_created_at', 'test_updated_at',
                                 'test_deleted_at')

        with stdout_redirect(six.StringIO()) as new_stdout:
            with mock.patch.object(
                    broker.Broker, 'create_broker') as mock_create_broker:

                mock_create_broker.return_value = fake_broker

                self.cue_manage_broker.add(broker_name, active_status)

        new_stdout.seek(0)
        std_out = new_stdout.read().strip()
        fake_broker_dict = fake_broker.__dict__

        for key in fake_broker_dict:
            self.assertIn(fake_broker_dict[key], std_out)

    def test_broker_list(self):
        """Test 'cue-manage broker list'

        Mocks the cue/objects/Broker.py get_brokers call to return a fake list
        of objects with specific attributes and asserts that that list of
        objects is printed to std_out.
        """

        fake_broker1 = FakeBroker('foo_id', 'foo_name', 'foo_active',
                               'foo_created_at', 'foo_updated_at',
                               'foo_deleted_at')
        fake_broker2 = FakeBroker('bar_id', 'bar_name', 'bar_active',
                               'bar_created_at', 'bar_updated_at',
                               'bar_deleted_at')

        with stdout_redirect(six.StringIO()) as new_stdout:
            with mock.patch.object(
                    broker.Broker, 'get_brokers') as mock_get_brokers:

                mock_get_brokers.return_value = [fake_broker1, fake_broker2]

                self.cue_manage_broker.list()

        new_stdout.seek(0)
        std_out = new_stdout.read().strip()

        fb1_dict = fake_broker1.__dict__
        fb2_dict = fake_broker2.__dict__

        for key in fb1_dict:
            self.assertIn(fb1_dict[key], std_out)
        for key in fb2_dict:
            self.assertIn(fb2_dict[key], std_out)

    @mock.patch('cue.objects.broker.Broker.delete_broker')
    def test_broker_delete(self, mock_delete_broker):
        """Test 'cue-manage broker delete'

        Mocks the cue/objects/broker.py delete_broker() function and asserts
        that it received the context from cue-manage
        """

        broker_name = "test_broker"
        self.cue_manage_broker.delete(broker_name)

        mock_delete_broker.assert_called_once_with(
            self.cue_manage_broker.context)

    @mock.patch('cue.objects.broker.Broker.update_broker')
    def test_broker_update(self, mock_update_broker):
        """Test 'cue-manage broker update'

        Mocks the cue/objects/broker.py update_broker() function and asserts
        that it received the context from cue-manage
        """
        broker_id = "test_broker_id"
        broker_name = "test_broker_name"
        broker_active = "True"

        self.cue_manage_broker.update(broker_id, broker_name, broker_active)
        mock_update_broker.assert_called_once_with(
            self.cue_manage_broker.context)

    @mock.patch(
        'cue.objects.broker_metadata.BrokerMetadata.create_broker_metadata')
    def test_broker_add_metadata(self, mock_add_metadata):
        """Test 'cue-manage broker add_metadata'

        Mocks the cue/objects/broker_metadata.py create_broker_metadata()
        function and asserts that it received the context from cue-manage
        """

        broker_id = "test_broker_id"
        image_id = "test_image_id"
        broker_sec_group = "test_sec_group"

        self.cue_manage_broker.add_metadata(broker_id,
                                            image_id,
                                            broker_sec_group)
        mock_add_metadata.assert_called_with(self.cue_manage_broker.context)

    def test_broker_add_metadata_invalid_values(self):
        """Test 'cue-manage broker add_metadata'

        Confirms that a call to add_metadata with invalid arguments
        will result in an Invalid exception.
        """

        broker_id = None
        image_id = None
        broker_sec_group = None

        self.assertRaises(exception.Invalid,
                          self.cue_manage_broker.add_metadata,
                          broker_id,
                          image_id,
                          broker_sec_group)

    def test_broker_list_metadata(self):
        """Test 'cue-manage broker list_metadata''

        Mocks the cue/objects/broker_metadata.py
        get_broker_metadata_by_broker_id() function and asserts that it
        received the context from cue-manage
        """

        fake_broker1 = FakeBrokerMetadata('foo_id', 'foo_broker_id', 'foo_key',
                               'foo_value', 'foo_created_at', 'foo_updated_at',
                               'foo_deleted_at')
        fake_broker2 = FakeBrokerMetadata('bar_id', 'bar_broker_id', 'bar_key',
                               'bar_value', 'bar_created_at', 'bar_updated_at',
                               'bar_deleted_at')

        with stdout_redirect(six.StringIO()) as new_stdout:
            with mock.patch.object(
                    broker_metadata.BrokerMetadata,
                    'get_broker_metadata_by_broker_id') as mock_get_brokers:

                mock_get_brokers.return_value = [fake_broker1, fake_broker2]

                self.cue_manage_broker.list_metadata("test_broker_id")

        new_stdout.seek(0)
        std_out = new_stdout.read().strip()

        fb1_dict = fake_broker1.__dict__
        fb2_dict = fake_broker2.__dict__

        for key in fb1_dict:
            self.assertIn(fb1_dict[key], std_out)
        for key in fb2_dict:
            self.assertIn(fb2_dict[key], std_out)

    @mock.patch(
        'cue.objects.broker_metadata.BrokerMetadata.delete_broker_metadata')
    def test_broker_delete_metadata(self, mock_delete_metadata):
        """Test 'cue-manage broker delete_metadata'

        Mocks the cue/objects/broker.py delete_metadata() function and asserts
        that it received the context from cue-manage
        """

        broker_metadata_id = "test_metadata_id"
        self.cue_manage_broker.delete_metadata(broker_metadata_id)

        mock_delete_metadata.assert_called_once_with(
            self.cue_manage_broker.context)
