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


MONITOR_OPTS = [
    cfg.IntOpt('loop_interval_seconds',
               help='How often Cluster Status is checked.',
               default=60)
]

opt_group = cfg.OptGroup(
    name='cue_monitor',
    title='Options for cue-monitor.'
)

CONF.register_group(opt_group)
CONF.register_opts(MONITOR_OPTS, group='cue_monitor')


def list_opts():
    return [('cue_monitor', MONITOR_OPTS)]