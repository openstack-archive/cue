# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import os_tasklib

from cue.common.i18n import _LW  # noqa
from cue.openstack.common import log as logging


LOG = logging.getLogger(__name__)


class CreateVm(os_tasklib.BaseTask):
    """CreateVm Task

    This task interfaces with Nova API and creates a VM based on parameters
    provided to the Task.

    """

    def execute(self, name, image, flavor, meta=None, files=None,
               reservation_id=None, min_count=None,
               max_count=None, security_groups=None, userdata=None,
               key_name=None, availability_zone=None,
               block_device_mapping=None, block_device_mapping_v2=None,
               nics=None, scheduler_hints=None,
               config_drive=None, disk_config=None, tx_id=None, **kwargs):
        """main execute method

        :param name: Something to name the server.
        :type name: string
        :param image: UUID of VM Image to boot with.
        :type image: string
        :param flavor: UUID of VM flavor to boot onto.
        :type flavor: string
        :param meta: A dict of arbitrary key/value metadata to store for this
                     server. A maximum of five entries is allowed, and both
                     keys and values must be 255 characters or less.
        :type meta: dict
        :param files: A dict of files to overrwrite on the server upon boot.
                      Keys are file names (i.e. ``/etc/passwd``) and values
                      are the file contents (either as a string or as a
                      file-like object). A maximum of five entries is allowed,
                      and each file must be 10k or less.
        :type files: dict
        :param userdata: user data to pass to be exposed by the metadata
                         server this can be a file type object as well or a
                         string.
        :type userdata: dict
        :param reservation_id: a UUID for the set of servers being requested.
        :type reservation_id: string
        :param key_name: (optional extension) name of previously created
                         keypair to inject into the instance.
        :type key_name: string
        :param availability_zone: Name of the availability zone for instance
                                  placement.
        :type availability_zone: string
        :param block_device_mapping: (optional extension) A dict of block
                                     device mappings for this server.
        :type block_device_mapping: dict
        :param block_device_mapping_v2: (optional extension) A dict of block
                                        device mappings for this server.
        :type block_device_mapping_v2: dict
        :param nics:  (optional extension) an ordered list of nics to be
                      added to this server, with information about
                      connected networks, fixed IPs, port etc.
        :type nics: list
        :param scheduler_hints: (optional extension) arbitrary key-value pairs
                                specified by the client to help boot an
                                instance
        :type scheduler_hints: dict
        :param config_drive: (optional extension) value for config drive
                             either boolean, or volume-id
        :type config_drive: string
        :param disk_config: (optional extension) control how the disk is
                            partitioned when the server is created.  possible
                            values are 'AUTO' or 'MANUAL'.
        :type disk_config: string
        :return: VM record provided by Nova
        :rtype: dict
        """

        new_vm = self.os_client.servers.create(
            name=name,
            image=image,
            flavor=flavor,
            meta=meta,
            files=files,
            reservation_id=reservation_id,
            min_count=min_count,
            max_count=max_count,
            security_groups=security_groups,
            userdata=userdata,
            key_name=key_name,
            availability_zone=availability_zone,
            block_device_mapping=block_device_mapping,
            block_device_mapping_v2=block_device_mapping_v2,
            nics=nics,
            scheduler_hints=scheduler_hints,
            config_drive=config_drive,
            disk_config=disk_config
        )
        return new_vm.to_dict()

    def revert(self, **kwargs):
        if kwargs.get('tx_id'):
            LOG.warning(_LW("%(tx_id)s Create VM failed %(result)s") %
                        {'tx_id': kwargs['tx_id'], 'result': kwargs['result']})
        else:
            LOG.warning(_LW("Create VM failed %s") % kwargs['result'])
