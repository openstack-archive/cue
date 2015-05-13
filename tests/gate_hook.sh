#!/bin/bash

set -ex

pushd $BASE/new/devstack

export ENABLED_SERVICES=cue,cue-api,cue-worker,zookeeper,dib
export PROJECTS="stackforge/cue-dashboard openstack/diskimage-builder $PROJECTS"
export DEVSTACK_GATE_NEUTRON=1

echo "DEST=/opt/stack/new" >> $BASE/new/devstack/localrc
echo "CUE_MANAGEMENT_KEY=cue-mgmt-key" >> $BASE/new/devstack/localrc

popd

# Run DevStack Gate
$BASE/new/devstack-gate/devstack-vm-gate.sh
