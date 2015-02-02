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


import logging
import sys

import eventlet
import oslo.config.cfg as cfg
import oslo_log.log as log

from cue.common.i18n import _LI  # noqa
import cue.common.service as cue_service
import cue.openstack.common.service as os_service
import cue.taskflow.service as tf_service


eventlet.monkey_patch(os=False)


WORKER_OPTS = [
    cfg.IntOpt('count',
               help="Number of worker processes to spawn",
               default=10)
]

opt_group = cfg.OptGroup(
    name='worker',
    title='Options for cue worker'
)

cfg.CONF.register_group(opt_group)
cfg.CONF.register_opts(WORKER_OPTS, group=opt_group)


def main():
    # Initialize environment
    CONF = cfg.CONF
    cue_service.prepare_service(sys.argv)

    # Log configuration and other startup information
    LOG = log.getLogger(__name__)
    LOG.info(_LI("Starting cue workers"))
    LOG.info(_LI("Configuration:"))
    CONF.log_opt_values(LOG, logging.INFO)

    cue_worker = tf_service.ConductorService.create("cue-worker")
    #cue_worker.start()
    launcher = os_service.launch(service=cue_worker, workers=CONF.worker.count)
    launcher.wait()


if __name__ == "__main__":
    sys.exit(main())
