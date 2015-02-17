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

import base_task as base_task


class UpdateClusterStatus(base_task.BaseTask):
    status_revert_pairs = {
        'BUILDING': 'FAILED'
    }

    def execute(self, cluster_status, **kwargs):
        print("Update Cluster Status to %s" % cluster_status)

    def revert(self, *args, **kwargs):
        if kwargs['cluster_status'] in UpdateClusterStatus.status_revert_pairs:
            print("Update Cluster Status to %s"
                  % UpdateClusterStatus.status_revert_pairs[kwargs['cluster_status']])