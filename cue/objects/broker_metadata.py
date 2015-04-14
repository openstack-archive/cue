# Copyright 2014 Hewlett-Packard Development Company, L.P.
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

from cue.db import api as db_api
from cue.objects import base
from cue.objects import utils as obj_utils


class BrokerMetadata(base.CueObject):
    dbapi = db_api.get_instance()

    fields = {
        'id': obj_utils.str_or_none,
        'broker_id': obj_utils.str_or_none,
        'key': obj_utils.str_or_none,
        'value': obj_utils.str_or_none,
        'deleted': obj_utils.bool_or_none,
        'created_at': obj_utils.datetime_or_str_or_none,
        'updated_at': obj_utils.datetime_or_str_or_none,
        'deleted_at': obj_utils.datetime_or_str_or_none,
    }

    @staticmethod
    def _from_db_object(broker_metadata, db_broker_metadata):
        """Convert a database object to a universal brokerMetadata object."""
        for field in BrokerMetadata.fields:
            broker_metadata[field] = db_broker_metadata[field]
        return broker_metadata

    def create_broker_metadata(self, context):
        """Creates a new broker metadata.

       :param context: request context object

       """
        metadata_values = self.as_dict()
        db_broker = self.dbapi.create_broker_metadata(context, metadata_values)

        self._from_db_object(self, db_broker)

    def delete_broker_metadata(self, context):
        """Deletes a BrokerMetadata object for specified broker_id.

        :param context: request context object

        """
        self.dbapi.delete_broker_metadata(context, self.id)

    @classmethod
    def get_broker_metadata_by_broker_id(cls, context, broker_id):
        """Returns a list of BrokerMetadata objects for specified broker_id.

        :param context: request context object
        :param broker_id: broker id
        :returns: a list of :class:'BrokerMetadata' object

        """
        db_broker_metadata = cls.dbapi.get_broker_metadata_by_broker_id(
            context, broker_id)

        return [BrokerMetadata._from_db_object(BrokerMetadata(), obj)
                for obj in db_broker_metadata]

    @classmethod
    def get_image_id_by_broker_name(cls, context, broker_name):
        """Returns a image_id for the broker

        :param context: request context object
        :param: broker name

        """
        image_id = cls.dbapi.get_image_id_by_broker_name(context, broker_name)

        return image_id