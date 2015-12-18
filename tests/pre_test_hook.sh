#!/bin/bash

set -ex

# Install cue devstack integration
pushd $BASE/new/cue/devstack

cp local.sh $BASE/new/devstack
cp plugin.sh $BASE/new/devstack

for f in lib/*; do
    if [ ! -e "$BASE/new/devstack/$f" ]; then
        echo "Installing: $f"
        cp -r $f $BASE/new/devstack/$f
    fi
done

popd