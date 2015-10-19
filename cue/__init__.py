# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Author: Endre Karlson <endre.karlson@hp.com>
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
import os.path

from oslo_config import cfg
from oslo_log import log

log.register_options(cfg.CONF)

DEFAULT_OPTS = [
    cfg.StrOpt('pybasedir',
               default=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                    '../')),
               help='Directory where the cue python module is installed'),
    cfg.StrOpt('state-path', default='/var/lib/cue',
               help='Top-level directory for maintaining cue\'s state'),
    cfg.StrOpt('rabbit_port',
               default='5672',
               help='The port to access RabbitMQ AMQP interface on a clustered'
                    'vm'),
    cfg.StrOpt('os_security_group',
               default=None,
               help='The default Security Group to use for VMs created as '
                    'part of a cluster'),
    cfg.StrOpt('management_network_id',
               default=None,
               help='The id representing the management network '),
    cfg.StrOpt('default_broker_name',
               default='rabbitmq',
               help='The name of the default broker image')
]

cfg.CONF.register_opts(DEFAULT_OPTS)

def list_opts():
    return [('DEFAULT', DEFAULT_OPTS)]