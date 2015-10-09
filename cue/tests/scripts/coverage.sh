#!/bin/bash
#
# Copyright 2015: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

set -x

COVERAGE_PERCENT_THRESHOLD=80

# Stash uncommited changes, checkout master and save coverage report
uncommited=$(git status --porcelain | grep -v "^??")
[[ -n $uncommited ]] && git stash > /dev/null
git checkout HEAD^

baseline_report=$(mktemp -t rally_coverageXXXXXXX)
python setup.py testr --coverage --testr-args="$*"
if [ $? -eq 0 ]; then
    coverage report > $baseline_report
    baseline_missing=$(awk 'END { print $3 }' $baseline_report)
else
    baseline_missing=''
fi

# Checkout back and unstash uncommited changes (if any)
git checkout -
[[ -n $uncommited ]] && git stash pop > /dev/null

# Generate and save coverage report
current_report=$(mktemp -t rally_coverageXXXXXXX)
python setup.py testr --coverage --testr-args="$*" || exit $?
coverage report > $current_report
current_missing=$(awk 'END { print $3 }' $current_report)
current_percent_coverage=$(awk 'END { print $6 }' $current_report | tr -d '%')

echo current_missing: $current_missing
echo current_percent_coverage: $current_percent_coverage
echo baseline_missing: $baseline_missing

if [ -z $baseline_missing ] &&
   [ $current_percent_coverage -gt $COVERAGE_PERCENT_THRESHOLD ];
then
    echo "Coverage is : ${current_percent_coverage} %"
    exit_code=0
else
    python cue/tests/scripts/diff_coverage.py $baseline_report $current_report
    exit_code=$?
fi

rm $baseline_report $current_report
exit $exit_code
