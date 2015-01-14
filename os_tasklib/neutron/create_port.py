# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
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


__author__ = 'sputnik13'

from os_tasklib import BaseTask


class CreatePort(BaseTask):
    default_provides = 'neutron_port_id'

    def execute(self, **kwargs):
        print "Create Neutron Port"
        return "RANDOM_NEUTRON_PORT_ID"

    def revert(self, **kwargs):
        print "Delete Neutron Port %s" % kwargs['result']
