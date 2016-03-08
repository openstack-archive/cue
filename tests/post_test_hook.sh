#!/bin/bash

set -ex

cd /opt/stack/new/cue/tests/integration

# Run the Cue Tempest tests
sudo -H ./run_tests.sh
