
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
from cue.db.sqlalchemy import api as sqlalchemy_api
from cue.db.sqlalchemy import models
from cue import objects
from cue.tests.functional import base
from cue.tests.functional import utils as func_utils
from cue.tests import utils as test_utils

from sqlalchemy.orm import exc as sql_exception


class BrokerObjectsTests(base.FunctionalTestCase):
    dbapi = db_api.get_instance()

    def create_object_broker(self, **kw):
        """Create a broker object."""
        test_broker_dict = func_utils.get_test_broker_dict(**kw)
        new_broker = objects.Broker(**test_broker_dict)
        self.validate_broker_values(test_broker_dict, new_broker)
        new_broker.create_broker(self.context)
        # retrieve created broker
        broker_query = sqlalchemy_api.model_query(
            self.context, models.Broker).filter_by(id=test_broker_dict['id'])
        db_broker = broker_query.one()
        broker_obj = objects.Broker._from_db_object(objects.Broker(),
                                                    db_broker)
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
        broker_dict = func_utils.get_test_broker_dict()
        broker_object = objects.Broker(**broker_dict)
        self.validate_broker_values(broker_dict, broker_object)

    def test_broker_db_to_object_to_db(self):
        """Tests Broker db object conversion to Broker object and back

        to db object.
        """
        broker_dict = func_utils.get_test_broker_dict()
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
        test_broker_dict = func_utils.get_test_broker_dict()
        new_broker = objects.Broker(**test_broker_dict)
        self.validate_broker_values(new_broker, test_broker_dict)
        retrieved_broker = new_broker.create_broker(self.context)

        self.validate_broker_values(new_broker, retrieved_broker)

    def test_update_broker(self):
        """Tests update broker from Broker objects API."""
        new_broker = self.create_object_broker()
        new_broker.name = 'rabbit1.0'
        new_broker.active = False
        new_broker.update_broker(self.context)

        # retrieve updated broker
        broker_query = sqlalchemy_api.model_query(
            self.context, models.Broker).filter_by(id=new_broker.id)
        updated_broker = broker_query.one()

        self.assertEqual('rabbit1.0', updated_broker.name)
        self.assertFalse(updated_broker.active)

    def test_get_brokers(self):
        """Tests getting all brokers from Broker objects API."""
        # delete existing default broker
        existing_broker = objects.Broker.get_brokers(self.context)
        existing_broker[0].delete_broker(self.context)

        # create new brokers
        new_broker_1 = self.create_object_broker(
            id='0e8e643e-eeb9-11e4-90ec-1681e6b88ec1', name='rabbit1.0')
        new_broker_2 = self.create_object_broker(
            id='ea1c6010-eeb8-11e4-90ec-1681e6b88ec1', name='rabbit2.0')

        broker_list = objects.Broker.get_brokers(self.context)

        # check for the list length
        self.assertEqual(2, len(broker_list), "Invalid number of brokers "
                                              "returned")
        for broker in broker_list:
            if broker.id == new_broker_1.id:
                self.validate_broker_values(new_broker_1, broker)
            else:
                self.validate_broker_values(new_broker_2, broker)

    def test_delete_broker(self):
        """Tests delete from Broker objects API."""
        new_broker = self.create_object_broker()
        new_broker.delete_broker(self.context)

        # try to retrieve deleted broker
        broker_query = sqlalchemy_api.model_query(
            self.context, models.Broker).filter_by(id=new_broker.id)

        self.assertRaises(sql_exception.NoResultFound, broker_query.one)