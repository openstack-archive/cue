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
Tests for cue broker_metadata object.
"""
import uuid

from cue.common import exception
from cue.db import api as db_api
from cue.db.sqlalchemy import models
from cue import objects
from cue.tests.functional import base
from cue.tests.functional import utils as func_utils
from cue.tests import utils as test_utils


class BrokerObjectsTests(base.FunctionalTestCase):
    dbapi = db_api.get_instance()

    def create_object_broker_metadata(self, broker_id, **kw):
        """Create broker_metadata object for the given broker."""
        test_metadata_dict = func_utils.get_test_broker_metadata_dict(
            broker_id=broker_id, **kw)
        new_broker_metadata = objects.BrokerMetadata(**test_metadata_dict)
        self.validate_broker_metadata_values(new_broker_metadata,
                                             test_metadata_dict)
        new_broker_metadata.create_broker_metadata(self.context)
        return new_broker_metadata

    def validate_broker_metadata_values(self, metadata_ref, metadata_cmp):
        """Validate Broker_Metadata Object fields."""
        self.assertEqual(metadata_ref.id if hasattr(metadata_ref, "id") else
                         metadata_ref["id"],
                         metadata_cmp.id if hasattr(metadata_cmp, "id") else
                         metadata_cmp["id"],
                         "Invalid broker id value")
        self.assertEqual(metadata_ref.broker_id if hasattr(metadata_ref,
                         "broker_id") else metadata_ref["broker_id"],
                         metadata_cmp.broker_id if hasattr(metadata_cmp,
                         "broker_id") else metadata_cmp["broker_id"],
                         "Invalid broker_id value")
        self.assertEqual(metadata_ref.key if hasattr(metadata_ref,
                         "key") else metadata_ref["key"],
                         metadata_cmp.key if hasattr(metadata_cmp,
                         "key") else metadata_cmp["key"],
                         "Invalid key value")
        self.assertEqual(metadata_ref.value if hasattr(metadata_ref,
                         "value") else metadata_ref["value"],
                         metadata_cmp.value if hasattr(metadata_cmp,
                         "value") else metadata_cmp["value"],
                         "Invalid value")
        self.assertTrue(test_utils.compare_dates(metadata_ref["created_at"],
                                                 metadata_cmp["created_at"]),
                        "Invalid created_at value")

        self.assertTrue(test_utils.compare_dates(metadata_ref["updated_at"],
                                                 metadata_cmp["updated_at"]),
                        "Invalid updated_at value")

        self.assertTrue(test_utils.compare_dates(metadata_ref["deleted_at"],
                                                 metadata_cmp["deleted_at"]),
                        "Invalid deleted_at value")

    def test_broker_metadata_object_generation(self):
        """Test BrokerMetadata Object generation from a metadata dictionary."""
        metadata_dict = func_utils.get_test_broker_metadata_dict()
        metadata_object = objects.BrokerMetadata(**metadata_dict)
        self.validate_broker_metadata_values(metadata_dict, metadata_object)

    def test_broker_metadata_db_to_object_to_db(self):
        """Tests BrokerMetadata db object conversion to BrokerMetadata object

        and back to db object.
        """
        metadata_dict = func_utils.get_test_broker_metadata_dict()
        db_metadata_object = models.BrokerMetadata()
        db_metadata_object.update(metadata_dict)
        object_metadata = objects.BrokerMetadata._from_db_object(
            objects.BrokerMetadata(), db_metadata_object)
        self.validate_broker_metadata_values(db_metadata_object,
                                             object_metadata)

        metadata_changes = object_metadata.obj_get_changes()
        db_metadata_object_2 = models.BrokerMetadata()
        db_metadata_object_2.update(metadata_changes)
        self.validate_broker_metadata_values(db_metadata_object,
                                             db_metadata_object_2)

    def test_create_broker_metadata(self):
        """Tests create broker_metadata from BrokerMetadata objects API."""
        new_broker = objects.Broker(**func_utils.get_test_broker_dict())
        new_broker.create_broker(self.context)
        test_metadata_dict = func_utils.get_test_broker_metadata_dict()
        new_broker_metadata = objects.BrokerMetadata(**test_metadata_dict)
        self.validate_broker_metadata_values(new_broker_metadata,
                                             test_metadata_dict)
        new_broker_metadata.create_broker_metadata(self.context)
        returned_broker_metadata = self.dbapi.get_broker_metadata_by_broker_id(
            self.context, new_broker.id)

        self.validate_broker_metadata_values(new_broker_metadata,
                                             returned_broker_metadata[0])

    def test_create_broker_metadata_for_nonexistent_broker(self):
        """Tests create broker_metadata for a nonexistent broker from

        BrokerMetadata objects API.
        """
        test_metadata_dict = func_utils.get_test_broker_metadata_dict(
            broker_id=str(uuid.uuid4()))
        new_broker_metadata = objects.BrokerMetadata(**test_metadata_dict)
        self.validate_broker_metadata_values(new_broker_metadata,
                                             test_metadata_dict)

        self.assertRaises(exception.NotFound,
                          new_broker_metadata.create_broker_metadata,
                          self.context)

    def test_get_broker_metadata_by_broker_id(self):
        """Tests get broker_metadata by broker_id from BrokerMetadata objects

         API.
         """
        new_broker = objects.Broker(**func_utils.get_test_broker_dict())
        new_broker.create_broker(self.context)
        broker_metadata_1 = self.create_object_broker_metadata(
            broker_id=new_broker.id)
        broker_metadata_2 = self.create_object_broker_metadata(
            broker_id=new_broker.id, id='a2dcf598-ef5d-11e4-90ec-1681e6b88ec1',
            key='SEC_GROUP', value='test')

        metadata_list = (objects.BrokerMetadata.
                         get_broker_metadata_by_broker_id(self.context,
                                                          new_broker.id))
        # check for the list length
        self.assertEqual(2, len(metadata_list), "Invalid number of "
                                                "broker_metadata returned")
        for metadata in metadata_list:
            if metadata.id == broker_metadata_1.id:
                self.validate_broker_metadata_values(broker_metadata_1,
                                                     metadata)
            else:
                self.validate_broker_metadata_values(broker_metadata_2,
                                                     metadata)

    def test_get_broker_metadata_by_invalid_broker_id(self):
        """Tests get broker_metadata from BrokerMetadata objects API with

        invalid broker id.
        """
        new_broker = objects.Broker(**func_utils.get_test_broker_dict())
        new_broker.create_broker(self.context)
        self.create_object_broker_metadata(broker_id=new_broker.id)
        invalid_broker_id = '17efe8ae-e93c-11e4-b02c-1681e6b88ec1'
        metadata = objects.BrokerMetadata.get_broker_metadata_by_broker_id(
            self.context, invalid_broker_id)

        self.assertListEqual([], metadata)

    def test_get_image_id_by_broker_name(self):
        """Tests get broker image_id by broker_name from BrokerMetadata objects

        API.
        """

        new_broker = objects.Broker(**func_utils.get_test_broker_dict())
        new_broker.create_broker(self.context)
        test_metadata_dict = func_utils.get_test_broker_metadata_dict()
        new_broker_metadata = objects.BrokerMetadata(**test_metadata_dict)
        self.validate_broker_metadata_values(new_broker_metadata,
                                             test_metadata_dict)
        new_broker_metadata.create_broker_metadata(self.context)

        image_id = objects.BrokerMetadata.get_image_id_by_broker_name(
            self.context, new_broker.name)

        self.assertEqual(image_id, new_broker_metadata.value)

    def test_get_image_id_by_nonexistent_broker_name(self):
        """Tests get broker image_id by nonexistent broker_name from

        BrokerMetadata objects API.
        """
        new_broker = objects.Broker(**func_utils.get_test_broker_dict())
        new_broker.create_broker(self.context)
        self.create_object_broker_metadata(broker_id=new_broker.id)
        invalid_broker_name = "kafka"
        self.assertRaises(exception.NotFound,
                          objects.BrokerMetadata.get_image_id_by_broker_name,
                          self.context, invalid_broker_name)

    def test_delete_broker_metadata(self):
        """Tests delete broker_metadata from BrokerMetadata objects API."""
        new_broker = objects.Broker(**func_utils.get_test_broker_dict())
        new_broker.create_broker(self.context)
        new_broker_metadata = self.create_object_broker_metadata(
            broker_id=new_broker.id)
        new_broker_metadata.delete_broker_metadata(self.context)
        metadata_returned = self.dbapi.get_broker_metadata_by_broker_id(
            self.context, new_broker_metadata.broker_id)

        self.assertListEqual([], metadata_returned)