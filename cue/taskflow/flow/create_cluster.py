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

import taskflow.patterns.linear_flow as linear_flow
import taskflow.retry as retry

import cue.client as client
import cue.taskflow.task as cue_task
import os_tasklib.cinder as cinder_task
import os_tasklib.common as common_task
import os_tasklib.neutron as neutron_task
import os_tasklib.nova as nova_task


def create_cluster():
    flow = linear_flow.Flow('creating vm').add(
        neutron_task.CreatePort(os_client=client.neutron_client(),
                                provides='neutron_port_id'),
        cinder_task.CreateVolume(os_client=client.cinder_client(),
                                 provides='cinder_volume_id'),
        nova_task.CreateVm(os_client=client.nova_client(),
                           provides='nova_vm_id'),
        linear_flow.Flow('wait for vm to become active',
                         retry=retry.Times(10)).add(
            nova_task.GetVmStatus(os_client=client.nova_client(),
                                  provides='vm_status'),
            common_task.CheckFor(rebind={'check_var': 'vm_status'},
                                 check_value='ACTIVE',
                                 timeout_seconds=1),
        ),
        cue_task.UpdateClusterStatus(cue_client="cue client"),

    )
    return flow
