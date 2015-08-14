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

from cue.taskflow.check_cluster_status import check_cluster_status   # noqa
from cue.taskflow.check_node_status import check_node_status         # noqa
from cue.taskflow.create_cluster import create_cluster               # noqa
from cue.taskflow.create_cluster_node import create_cluster_node     # noqa
from cue.taskflow.delete_cluster import delete_cluster               # noqa
from cue.taskflow.delete_cluster_node import delete_cluster_node     # noqa

from oslo_config import cfg

opt_group = cfg.OptGroup(
    name='flow_options',
    title='Options for taskflow flows.'
)

cfg.CONF.register_group(opt_group)
