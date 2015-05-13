#!/bin/bash

set -ex

pushd $BASE/new/devstack

export ENABLED_SERVICES=cue,cue-api,cue-worker,zookeeper

echo "DEST=/opt/stack/new" >> $BASE/new/devstack/localrc
echo "CUE_MANAGEMENT_KEY=cue-mgmt-key" >> $BASE/new/devstack/localrc

popd

# Run DevStack Gate
$BASE/new/devstack-gate/devstack-vm-gate.sh