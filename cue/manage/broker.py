# Copyright 2015 Hewlett-Packard Development Company, L.P.#
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

from cue.common import exception
from cue.common.i18n import _  # noqa
from oslo.config import cfg
from oslo.utils import strutils
from cliff import lister
import logging

from cue.manage import base
from cue import objects
from cue.db.sqlalchemy import models

LOG = logging.getLogger(__name__)

CONF = cfg.CONF


class BrokerCommands(base.Commands, lister.Lister):
    def __init__(self):
        super(BrokerCommands, self).__init__()

    @base.args('--type', dest='broker_type')
    @base.args('--active', dest='active_status')
    def add(self, broker_type, active_status):
        status = strutils.bool_from_string(active_status)
        broker_values = {
            'type': broker_type,
            'active_status': status,
        }
        broker = objects.Broker()
        broker.create_broker(broker_values)

    def list(self):
        broker_obj = objects.Broker()
        broker_list = broker_obj.get_brokers()
        for broker in broker_list:
            print broker.id, broker.active_status, broker.type

    def take_action(self, parsed_args):

        cols = self.columns
        return cols, (get_item_properties(s, cols) for s in broker_list)

    @base.args('--id', dest='broker_id')
    def delete(self, broker_id):
        broker_obj = objects.Broker()
        broker_obj.delete_broker(broker_id)

    @base.args('--id', dest='broker_id')
    @base.args('--type', nargs='?')
    @base.args('--status', nargs='?')
    def update(self, broker_id, type, status):
        broker_value = {}
        if status is not None:
            status = strutils.bool_from_string(status)
            broker_value['active_status'] = status
            print status
        if type is not None:
            broker_value['type'] = type

        broker_obj = objects.Broker()
        broker_obj.update_broker(broker_id, broker_value)

    @base.args('--id', dest='broker_id')
    @base.args('--image', dest='image_id', nargs='?')
    @base.args('--sec-group', dest='sec_group', nargs='?')
    def add_metadata(self, broker_id, image_id, sec_group):

        if image_id is not None:
            metadata_value = {
                'key': models.MetadataKey.IMAGE,
                'value': image_id,
                'broker_id': broker_id
            }
            metadata = objects.Broker_Metadata()
            metadata.add_broker_metadata(metadata_value)

        if sec_group is not None:
            metadata_value = {
                'key': models.MetadataKey.SEC_GROUP,
                'value': sec_group,
                'broker_id': broker_id
            }
            metadata = objects.Broker_Metadata()
            metadata.add_broker_metadata(metadata_value)

        if image_id is None and sec_group is None:
            raise exception.Invalid(_("Requires atleast one argument"))

    @base.args('--id', dest='broker_id')
    def list_metadata(self, broker_id):
        metadata = objects.Broker_Metadata()
        broker_metadata = metadata.get_broker_by_id(broker_id)

        for r in broker_metadata:
            print r.id, r.broker_id, r.key, r.value, r.deleted

    @base.args('--id', dest='broker_metadata_id')
    def delete_metadata(self, broker_metadata_id):
        broker_obj = objects.Broker_Metadata()
        broker_obj.delete_broker_metadata(broker_metadata_id)


def get_item_properties(item, fields, mixed_case_fields=[], formatters={}):
    """Return a tuple containing the item properties.

    :param item: a single dict resource
    :param fields: tuple of strings with the desired field names
    :param mixed_case_fields: tuple of field names to preserve case
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    row = []
    for field in fields:
        if field in mixed_case_fields:
            field_name = field.replace(' ', '_')
        else:
            field_name = field.lower().replace(' ', '_')
        data = item[field_name] if field_name in item else ''
        if field in formatters:
            row.append(formatters[field](data))
        else:
            row.append(data)
    return tuple(row)
