#!/bin/bash

set -ex

# Install cue devstack integration
pushd $BASE/new/cue/contrib/devstack

cp local.sh $BASE/new/devstack

popd
