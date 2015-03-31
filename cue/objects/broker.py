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


class Broker(base.CueObject):
    dbapi = db_api.get_instance()

    fields = {
        'id': obj_utils.str_or_none,
        'type': obj_utils.str_or_none,
        'active_status': obj_utils.bool_or_none,
        'deleted': obj_utils.bool_or_none,
    }

    @staticmethod
    def _from_db_object(broker, db_broker):
        """Convert a database object to a universal broker object."""
        for field in broker.fields:
            broker[field] = db_broker[field]
        return broker

    def create_broker(self, broker_values, context=None):
        """Creates a new broker.

       :param context: request context object
       :param broker_values: Dictionary of several required items
               ::

               {
                'type': obj_utils.str_or_none,
                'active_status': obj_utils.bool_or_none
               }
         """

        db_broker = self.dbapi.create_broker(broker_values, context)

        self._from_db_object(self, db_broker)

    @classmethod
    def get_brokers(cls, context=None):
        """Returns a list of Broker objects.

        :param context: request context object
        :returns: a list of :class:'Broker' object

        """
        db_brokers = cls.dbapi.get_brokers(context)
        return [Broker._from_db_object(Broker(), obj) for obj in db_brokers]

    @classmethod
    def delete_broker(cls, broker_id, context=None):
        """Deletes a Broker object for specified broker_id.

        :param broker_id: UUID of a broker
        :param context: request context object

        """
        cls.dbapi.delete_broker(broker_id, context)

    @classmethod
    def update_broker(cls, broker_id, broker_value, context=None):
        """Updates a Broker type/status for specified broker_id.

        :param broker_id: UUID of a broker
        :param broker_value: Dictionary of attribute values to be updated
        :param context: request context object

        """
        cls.dbapi.update_broker(broker_id, broker_value, context)