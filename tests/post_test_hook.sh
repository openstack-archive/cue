#!/bin/bash

set -ex

cd /opt/stack/new/cue/tests/integration
cp /opt/stack/new/cue/tests/integration/cue-integration.conf /etc/cue/cue-integration.conf
# Run the Cue Tempest tests
sudo ./run_tests.sh