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


from oslo.config import cfg
from oslo.utils import strutils
from oslo_log import log as logging
import prettytable

from cue.common import exception
from cue.common.i18n import _  # noqa
from cue.db.sqlalchemy import models
from cue.manage import base
from cue import objects

LOG = logging.getLogger(__name__)

CONF = cfg.CONF


class BrokerCommands(base.Commands):
    def __init__(self):
        super(BrokerCommands, self).__init__()

    @base.args('--name', dest='broker_name')
    @base.args('--active', dest='active')
    def add(self, broker_name, active):
        status = strutils.bool_from_string(active)
        broker_values = {
            'name': broker_name,
            'active': status,
        }
        broker = objects.Broker()
        broker.create_broker(broker_values)

    def list(self):
        broker_obj = objects.Broker()
        broker_list = broker_obj.get_brokers()
        list_table = prettytable.PrettyTable(["Broker id", "Broker Name",
                                              "Active", "Created Time",
                                              "Updated Time", "Deleted Time"])
        for broker in broker_list:
            list_table.add_row([broker.id, broker.name, broker.active,
                                broker.created_at, broker.updated_at,
                                broker.deleted_at])
        print(list_table)

    @base.args('--id', dest='broker_id')
    def delete(self, broker_id):
        broker_obj = objects.Broker()
        broker_obj.delete_broker(broker_id)

    @base.args('--id', dest='broker_id')
    @base.args('--name', nargs='?')
    @base.args('--active', nargs='?')
    def update(self, broker_id, name, active):
        broker_value = {}
        if active is not None:
            active = strutils.bool_from_string(active)
            broker_value['active'] = active
        if type is not None:
            broker_value['name'] = name

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
            metadata = objects.BrokerMetadata()
            metadata.add_broker_metadata(metadata_value)

        if sec_group is not None:
            metadata_value = {
                'key': models.MetadataKey.SEC_GROUP,
                'value': sec_group,
                'broker_id': broker_id
            }
            metadata = objects.BrokerMetadata()
            metadata.add_broker_metadata(metadata_value)

        if image_id is None and sec_group is None:
            raise exception.Invalid(_("Requires atleast one argument"))

    @base.args('--id', dest='broker_id')
    def list_metadata(self, broker_id):
        metadata = objects.BrokerMetadata()
        broker_metadata = metadata.get_broker_metadata_by_broker_id(broker_id)
        list_table = prettytable.PrettyTable(["Broker_Metadata id",
                                             "Broker id", "Key", "Value",
                                              "Created Time", "Updated Time",
                                              "Deleted Time"])

        for broker in broker_metadata:
            list_table.add_row([broker.id, broker.broker_id, broker.key,
                                broker.value, broker.created_at,
                                broker.updated_at, broker.deleted_at])
        print(list_table)

    @base.args('--id', dest='broker_metadata_id')
    def delete_metadata(self, broker_metadata_id):
        broker_obj = objects.BrokerMetadata()
        broker_obj.delete_broker_metadata(broker_metadata_id)
