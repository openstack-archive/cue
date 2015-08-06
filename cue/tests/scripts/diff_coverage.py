# -*- encoding: utf-8 -*-
#
# Copyright © 2015 Hewlett-Packard
#
## Licensed under the Apache License, Version 2.0 (the "License"); you may
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

import pprint
import sys

"""
This script assumes 2 variables are passed to it,
the first is the "old" coverage report, the second
is the "new" coverage report.  This script will
provide details on what file(s) increased in the
number of Missing lines.
"""


def parse_coverage_report(report_filename):
    raw = open(report_filename).read()
    lines = raw.split('\n')
    heading = lines[0].split()
    cover_details = map(lambda l: l.split(), lines[2:-3])
    cover_details = map(lambda item: (item[0],
                                      dict(zip(heading[1:], item[1:]))),
                        cover_details)
    return dict(cover_details)


def main():
    old_cover_file = sys.argv[1]
    new_cover_file = sys.argv[2]

    old_cover_details = parse_coverage_report(old_cover_file)
    new_cover_details = parse_coverage_report(new_cover_file)

    new_files = set(new_cover_details.keys()) - set(old_cover_details.keys())
    existing_files = (set(old_cover_details.keys()) &
                      set(new_cover_details.keys()))

    bad_new_files = filter(
        lambda item: new_cover_details[item]['Miss'] > '0',
        new_files)
    bad_existing_files = dict(
        filter(
            lambda item: item[0] in existing_files and
            item[1]['Miss'] > old_cover_details[item[0]]['Miss'],
            new_cover_details.items()))

    rc = 0

    if len(bad_new_files) > 0:
        print("The following files are new and have missing coverage:\n")
        pprint.pprint(bad_new_files)
        print("\n\n")
        rc = -1

    if len(bad_existing_files) > 0:
        print("The following files have regressed in coverage:\n")
        pprint.pprint(bad_existing_files)
        rc = -1

    if rc == 0:
        print("Coverage looks good.")

    return rc

if __name__ == '__main__':
    sys.exit(main())
