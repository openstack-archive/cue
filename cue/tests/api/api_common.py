# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Authors: Davide Agnello <davide.agnello@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Copyright [2014] Hewlett-Packard Development Company, L.P.
# limitations under the License.
"""
Common API base class to controller test classes.
"""

import cue.tests.api as api_base


class ApiCommon(api_base.FunctionalTest):
    cluster_name = "test-cluster"

    def validate_cluster_values(self, cluster_reference, cluster_compare):
        self.assertEqual(cluster_reference.id, cluster_compare["id"],
                         "Invalid cluster id value")
        self.assertEqual(cluster_reference.network_id,
                         cluster_compare["network_id"],
                         "Invalid cluster network_id value")
        self.assertEqual(cluster_reference.name, cluster_compare["name"],
                         "Invalid cluster name value")
        self.assertEqual(cluster_reference.status, cluster_compare["status"],
                         "Invalid cluster status value")
        self.assertEqual(cluster_reference.flavor, cluster_compare["flavor"],
                         "Invalid cluster flavor value")
        self.assertEqual(cluster_reference.size, cluster_compare["size"],
                         "Invalid cluster size value")
        self.assertEqual(cluster_reference.volume_size,
                         cluster_compare["volume_size"],
                         "Invalid cluster volume_size value")
        self.assertEqual(unicode(cluster_reference.created_at.isoformat()),
                         cluster_compare["created_at"],
                         "Invalid cluster created_at value")
        self.assertEqual(unicode(cluster_reference.updated_at.isoformat()),
                         cluster_compare["updated_at"],
                         "Invalid cluster updated_at value")