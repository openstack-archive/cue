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

"""cue-monitor

cue-monitor is responsible for actively monitoring cluster statuses
"""
import logging

from oslo_config import cfg
import oslo_log.log as log
from oslo_service import service as openstack_service

from cue.common.i18n import _LI  # noqa
import cue.common.service as cue_service
import cue.monitor.monitor_service as cue_monitor_service

import sys


def main():

    CONF = cfg.CONF
    cue_service.prepare_service(sys.argv)

    # Log configuration and other startup information
    LOG = log.getLogger(__name__)
    LOG.info(_LI("Starting cue-monitor"))
    LOG.info(_LI("Configuration:"))
    CONF.log_opt_values(LOG, logging.INFO)

    monitor = cue_monitor_service.MonitorService()
    launcher = openstack_service.launch(CONF, monitor)
    launcher.wait()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
