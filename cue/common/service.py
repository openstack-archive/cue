# -*- encoding: utf-8 -*-
#
# Copyright 2014-2015 Hewlett-Packard Development Company, L.P.
# Copyright © 2012 eNovance <licensing@enovance.com>
#
# Author: Julien Danjou <julien@danjou.info>
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

import socket
import sys

from oslo_config import cfg
from oslo_log import log


service_opts = [
    cfg.IntOpt('periodic_interval',
               default=60,
               help='Seconds between running periodic tasks.'),
    cfg.StrOpt('host',
               default=socket.getfqdn(),
               help='Name of this node.  This can be an opaque identifier.  '
               'It is not necessarily a hostname, FQDN, or IP address. '
               'However, the node name must be valid within '
               'an AMQP key, and if using ZeroMQ, a valid '
               'hostname, FQDN, or IP address.'),
]


CONF = cfg.CONF

CONF.register_opts(service_opts)


LOG = log.getLogger(__name__)


def prepare_service(argv=None):

    log_levels = (CONF.default_log_levels +
                  ['stevedore=INFO', 'keystoneclient=INFO'])
    log.set_defaults(default_log_levels=log_levels)
    if argv is None:
        argv = sys.argv
    CONF(argv[1:], project='cue')
    log.setup(CONF, 'cue')


def list_opts():
    return [('DEFAULT', service_opts)]
