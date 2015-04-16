
# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Copyright [2014] Hewlett-Packard Development Company, L.P.
# limitations under the License.
"""
Tests for cue broker object.
"""
from cue.db import api as db_api
from cue.db.sqlalchemy import models
from cue import objects
from cue.tests.functional import base
from cue.tests.functional import utils as func_utils
from cue.tests import utils as test_utils


class BrokerObjectsTests(base.FunctionalTestCase):
    dbapi = db_api.get_instance()

    def create_object_broker(self):
        """Create a broker object."""
        test_broker_dict = func_utils.get_test_broker()
        new_broker = objects.Broker(**test_broker_dict)
        self.validate_broker_values(test_broker_dict, new_broker)
        new_broker.create_broker(self.context)
        db_brokers = self.dbapi.get_brokers(self.context)
        # select the created broker from list of brokers
        for db_broker in db_brokers:
            if db_broker.id == test_broker_dict['id']:
                broker_obj = objects.Broker._from_db_object(objects.Broker(),
                                                            db_broker)
                break
        return broker_obj

    def validate_broker_values(self, broker_ref, broker_cmp):
        """Validate Broker Object fields."""
        self.assertEqual(broker_ref.id if hasattr(broker_ref, "id") else
                         broker_ref["id"],
                         broker_cmp.id if hasattr(broker_cmp, "id") else
                         broker_cmp["id"],
                         "Invalid broker id value")
        self.assertEqual(broker_ref.name if hasattr(broker_ref, "name")
                         else broker_ref["name"],
                         broker_cmp.name if hasattr(broker_cmp, "name")
                         else broker_cmp["name"],
                         "Invalid name value")
        self.assertEqual(broker_ref.active if hasattr(broker_ref,
                         "active") else broker_ref["active"],
                         broker_cmp.active if hasattr(broker_cmp,
                         "active") else broker_cmp["active"],
                         "Invalid active status")
        self.assertTrue(test_utils.compare_dates(broker_ref["created_at"],
                                                 broker_cmp["created_at"]),
                        "Invalid created_at value")

        self.assertTrue(test_utils.compare_dates(broker_ref["updated_at"],
                                                 broker_cmp["updated_at"]),
                        "Invalid updated_at value")

        self.assertTrue(test_utils.compare_dates(broker_ref["deleted_at"],
                                                 broker_cmp["deleted_at"]),
                        "Invalid deleted_at value")

    def test_broker_object_generation(self):
        """Test Broker Object generation from a broker dictionary object."""
        broker_dict = func_utils.get_test_broker()
        broker_object = objects.Broker(**broker_dict)
        self.validate_broker_values(broker_dict, broker_object)

    def test_broker_db_to_object_to_db(self):
        """Tests Broker db object conversion to Broker object and back

        to db object.
        """
        broker_dict = func_utils.get_test_broker()
        db_broker_object = models.Broker()
        db_broker_object.update(broker_dict)
        object_broker = objects.Broker._from_db_object(objects.Broker(),
                                                       db_broker_object)
        self.validate_broker_values(db_broker_object, object_broker)

        broker_changes = object_broker.obj_get_changes()
        db_broker_object_2 = models.Broker()
        db_broker_object_2.update(broker_changes)
        self.validate_broker_values(db_broker_object, db_broker_object_2)

    def test_create_broker(self):
        """Tests create broker from Broker objects API."""
        test_broker_dict = func_utils.get_test_broker()
        new_broker = objects.Broker(**test_broker_dict)
        self.validate_broker_values(new_broker, test_broker_dict)
        new_broker.create_broker(self.context)
        db_brokers = self.dbapi.get_brokers(self.context)
        # select the created broker from list of brokers
        for db_broker in db_brokers:
            if db_broker.id == test_broker_dict['id']:
                obj_broker = objects.Broker._from_db_object(objects.Broker(),
                                                            db_broker)
                break
        self.validate_broker_values(new_broker, obj_broker)

    def test_update_broker(self):
        """Tests update broker from Broker objects API."""
        new_broker = self.create_object_broker()
        new_broker.name = 'rabbit1.0'
        new_broker.active = False
        new_broker.update_broker(self.context)

        db_brokers = self.dbapi.get_brokers(self.context)
        # select the updates broker from list of brokers
        for db_broker in db_brokers:
            if db_broker.id == new_broker.id:
                updated_broker = objects.Broker._from_db_object(
                    objects.Broker(), db_broker)
                break

        self.assertEqual('rabbit1.0', updated_broker.name)
        self.assertEqual(False, updated_broker.active)

    def test_get_brokers(self):
        """Tests getting all brokers from Broker objects API."""
        new_broker = self.create_object_broker()
        broker_list = objects.Broker.get_brokers(self.context)

        for broker in broker_list:
            if broker.id == new_broker.id:
                obj_broker = objects.Broker._from_db_object(objects.Broker(),
                                                            broker)
                break

        self.validate_broker_values(new_broker, obj_broker)

    def test_delete_broker(self):
        """Tests delete from Broker objects API."""
        new_broker = self.create_object_broker()
        new_broker.delete_broker(self.context)

        db_brokers = self.dbapi.get_brokers(self.context)

        is_deleted = True
        # check to see if deleted broker is in list
        for db_broker in db_brokers:
            if db_broker.id == new_broker.id:
                is_deleted = False
                break

        self.assertTrue(is_deleted)