#!/bin/bash

set -ex

# Install cue devstack integration
pushd $BASE/new/cue/devstack

cp local.sh $BASE/new/devstack

popd
