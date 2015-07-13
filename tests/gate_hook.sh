#!/bin/bash

set -ex

pushd $BASE/new/devstack

export KEEP_LOCALRC=1
export ENABLED_SERVICES=cue,cue-api,cue-worker,zookeeper,dib
export PROJECTS="openstack/diskimage-builder openstack/cue-dashboard $PROJECTS"
export DEVSTACK_GATE_NEUTRON=1

echo "CUE_MANAGEMENT_KEY=cue-mgmt-key" >> $BASE/new/devstack/localrc
echo "CUE_TF_CREATE_CLUSTER_NODE_VM_ACTIVE_RETRY_COUNT=60" >> $BASE/new/devstack/localrc

popd

# Run DevStack Gate
$BASE/new/devstack-gate/devstack-vm-gate.sh
