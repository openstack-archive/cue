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
        'name': obj_utils.str_or_none,
        'active': obj_utils.bool_or_none,
        'deleted': obj_utils.bool_or_none,
        'created_at': obj_utils.datetime_or_str_or_none,
        'updated_at': obj_utils.datetime_or_str_or_none,
        'deleted_at': obj_utils.datetime_or_str_or_none,
    }

    @staticmethod
    def _from_db_object(broker, db_broker):
        """Convert a database object to a universal broker object."""
        for field in broker.fields:
            broker[field] = db_broker[field]
        return broker

    def create_broker(self, context):
        """Creates a new broker.

        :param context: request context object
        """
        broker_values = self.as_dict()
        db_broker = self.dbapi.create_broker(context, broker_values)

        self._from_db_object(self, db_broker)

    def delete_broker(self, context):
        """Deletes a Broker object for specified broker_id.

        :param context: request context object

        """
        self.dbapi.delete_broker(context, self.id)

    def update_broker(self, context):
        """Updates a Broker type/status for specified broker_id.

        :param context: request context object

        """
        broker_value = self.as_dict()
        self.dbapi.update_broker(context, self.id, broker_value)

    @classmethod
    def get_brokers(cls, context):
        """Returns a list of Broker objects.

        :param context: request context object
        :returns: a list of :class:'Broker' object

        """
        db_brokers = cls.dbapi.get_brokers(context)
        return [Broker._from_db_object(Broker(), obj) for obj in db_brokers]
