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
from oslo_config import cfg


CONF = cfg.CONF


TF_OPTS = [
    cfg.StrOpt('persistence_connection',
               help="Persistence connection.",
               default=None),

    cfg.StrOpt('coord_url',
               help="Coordinator connection string prefix.",
               default='zookeeper'),

    cfg.StrOpt('zk_hosts',
               help="Zookeeper jobboard hosts.",
               default="localhost"),

    cfg.StrOpt('zk_port',
               help="Zookeeper jobboard port.",
               default="2181"),

    cfg.StrOpt('zk_path',
               help="Zookeeper path for jobs.",
               default='/cue/taskflow'),

    cfg.IntOpt('zk_timeout',
               help="Zookeeper operations timeout.",
               default=10),

    cfg.StrOpt('jobboard_name',
               help="Board name.",
               default='cue'),

    cfg.StrOpt('engine_type',
               help="Engine type.",
               default='serial'),

    cfg.IntOpt('cluster_node_check_timeout',
               help="Number of seconds to wait between checks for node status",
               default=10),

    cfg.IntOpt('cluster_node_check_max_count',
               help="Number of times to check a node for status before "
               "declaring it FAULTED",
               default=30),

    cfg.BoolOpt('cluster_member_affinity',
           help="Affinity policy to provision cluster members in different hosts",
           default=False),
]

opt_group = cfg.OptGroup(
    name='taskflow',
    title='Options for taskflow.'
)

CONF.register_group(opt_group)
CONF.register_opts(TF_OPTS, group='taskflow')
