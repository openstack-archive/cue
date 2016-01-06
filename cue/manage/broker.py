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


from oslo_config import cfg
from oslo_utils import strutils
import prettytable

from cue.common import context as cue_context
from cue.common import exception
from cue.common.i18n import _  # noqa
from cue.db.sqlalchemy import models
from cue.manage import base
from cue import objects

CONF = cfg.CONF


class BrokerCommands(base.Commands):
    """Broker commands for accessing broker and broker_metadata tables.

    - To add a new broker use 'broker add'.
    - To add a new metadata for a broker; get broker_id using 'broker list'
      and use the id in the command 'broker add_metadata'.
    """
    def __init__(self):
        super(BrokerCommands, self).__init__()
        self.context = cue_context.RequestContext()

    @base.args('NAME', help="Broker name")
    @base.args('ACTIVE', help="Broker active status(boolean)")
    def add(self, broker_name, active):
        """Add a new broker."""
        status = strutils.bool_from_string(active)
        broker_values = {
            'name': broker_name,
            'active': status,
        }
        broker = objects.Broker(**broker_values)
        new_broker = broker.create_broker(self.context)

        new_broker_table = prettytable.PrettyTable(
            ["Broker id", "Broker Name", "Active", "Created Time",
             "Updated Time", "Deleted Time", ])
        new_broker_table.add_row(
            [new_broker.id, new_broker.name, new_broker.active,
             new_broker.created_at, new_broker.updated_at,
             new_broker.deleted_at])
        print(new_broker_table)
        return new_broker

    def list(self):
        """List all the brokers."""
        broker_list = objects.Broker.get_brokers(self.context)
        list_table = prettytable.PrettyTable(["Broker id", "Broker Name",
                                              "Active", "Created Time",
                                              "Updated Time", "Deleted Time",
                                              ])
        for broker in broker_list:
            list_table.add_row([broker.id, broker.name, broker.active,
                                broker.created_at, broker.updated_at,
                                broker.deleted_at])
        print(list_table)
        return broker_list

    @base.args('ID', help='Broker id')
    def delete(self, broker_id):
        """Delete a broker."""
        broker_id = {'id': broker_id}
        broker_obj = objects.Broker(**broker_id)
        broker_obj.delete_broker(self.context)

    @base.args('ID', help='Broker id')
    @base.args('--name', nargs='?', help='Broker name')
    @base.args('--active', nargs='?', help='Broker active status(boolean)')
    def update(self, broker_id, broker_name, active):
        """Update name/active field or both the fields for a given broker."""
        broker_value = {}
        if broker_name is not None:
            broker_value['name'] = broker_name
        if active is not None:
            active = strutils.bool_from_string(active)
            broker_value['active'] = active

        broker_value['id'] = broker_id
        broker_obj = objects.Broker(**broker_value)
        broker_obj.update_broker(self.context)

    @base.args('ID', help='Broker id')
    @base.args('--image', dest='image_id', nargs='?', help='Image id')
    @base.args('--sec-group', dest='sec_group', nargs='?',
               help='Security group')
    def add_metadata(self, broker_id, image_id, sec_group):
        """Add broker metadata - image and sec group for the given broker_id.

        """
        if image_id is not None:
            metadata_value = {
                'key': models.MetadataKey.IMAGE,
                'value': image_id,
                'broker_id': broker_id
            }
            metadata = objects.BrokerMetadata(**metadata_value)
            metadata.create_broker_metadata(self.context)

        if sec_group is not None:
            metadata_value = {
                'key': models.MetadataKey.SEC_GROUP,
                'value': sec_group,
                'broker_id': broker_id
            }
            metadata = objects.BrokerMetadata(**metadata_value)
            metadata.create_broker_metadata(self.context)

        if image_id is None and sec_group is None:
            raise exception.Invalid(_("Requires atleast one argument"))

    @base.args('ID', help='Broker id')
    def list_metadata(self, broker_id):
        """List broker metadata for the given broker_id."""
        broker_metadata = (
            objects.BrokerMetadata.
            get_broker_metadata_by_broker_id(self.context, broker_id))
        list_table = prettytable.PrettyTable(["Broker_Metadata id",
                                             "Broker id", "Key", "Value",
                                              "Created Time", "Updated Time",
                                              "Deleted Time"])

        for broker in broker_metadata:
            list_table.add_row([broker.id, broker.broker_id, broker.key,
                                broker.value, broker.created_at,
                                broker.updated_at, broker.deleted_at])
        print(list_table)
        return broker_metadata

    @base.args('ID', help='Broker metadata id')
    def delete_metadata(self, broker_metadata_id):
        """Delete broker metadata for the given broker_metadata_id."""
        broker_metadata_id = {'id': broker_metadata_id}
        broker_obj = objects.BrokerMetadata(**broker_metadata_id)
        broker_obj.delete_broker_metadata(self.context)
