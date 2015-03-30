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

from cue.common import policy
from cue.db import api as db_api
from cue.objects import base
from cue.objects import utils as obj_utils


class brokerMetadata(base.CueObject):
    dbapi = db_api.get_instance()

    fields = {
        'id': obj_utils.str_or_none,
        'broker_id': obj_utils.str_or_none,
        'key': obj_utils.str_or_none,
        'value': obj_utils.str_or_none,
        'deleted': obj_utils.bool_or_none,
    }

    @staticmethod
    def _from_db_object(broker_metadata, db_broker_metadata):
        """Convert a database object to a universal brokerMetadata object."""
        for field in brokerMetadata.fields:
            broker_metadata[field] = db_broker_metadata[field]
        return broker_metadata

    def add_broker_metadata(self, metadata_values, context=None):
        """Creates a new broker metadata.

       :param context: request context object
       :param metadata_values: Dictionary of several required items
               ::

               {
                'broker_id': UUID of a broker,
                'key': obj_utils.str_or_none,
                'value': obj_utils.str_or_none
               }
         """
        db_broker = self.dbapi.create_broker_metadata(metadata_values, context)

        self._from_db_object(self, db_broker)

    @classmethod
    def get_broker_by_id(cls, broker_id, context=None):
        """Returns a list of BrokerMetadata objects for specified broker_id.

        :param broker_id: UUID of a broker
        :param context: request context object
        :returns: a list of :class:'BrokerMetadata' object

        """
        db_broker_metadata = cls.dbapi.get_broker_by_id(broker_id, context)

        return [brokerMetadata._from_db_object(brokerMetadata(), obj)
                for obj in db_broker_metadata]

    @classmethod
    def delete_broker_metadata(cls, broker_metadata_id, context=None):
        """Deletes a BrokerMetadata object for specified broker_id.

        :param broker_metadata_id: UUID of a broker metadata
        :param context: request context object

        """
        cls.dbapi.delete_broker_metadata(broker_metadata_id, context)
