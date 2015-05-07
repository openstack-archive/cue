# Copyright 2015 Hewlett-Packard Development Company, L.P.
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
Cue test utilities.
"""
import iso8601


def compare_dates(datetime1, datetime2):
    """Compare datetime objects."""
    if datetime1 is not None and datetime1.utcoffset() is None:
        datetime1 = datetime1.replace(tzinfo=iso8601.iso8601.Utc())
    if datetime2 is not None and datetime2.utcoffset() is None:
        datetime2 = datetime2.replace(tzinfo=iso8601.iso8601.Utc())
    return datetime1 == datetime2


def validate_cluster_values(self, cluster_ref, cluster_cmp):
        """Validate cluster object fields."""
        self.assertEqual(cluster_ref.id if hasattr(cluster_ref, "id") else
                         cluster_ref["id"],
                         cluster_cmp.id if hasattr(cluster_cmp, "id") else
                         cluster_cmp["id"],
                         "Invalid cluster id value")
        self.assertEqual(cluster_ref.name if hasattr(cluster_ref, "name")
                         else cluster_ref["name"],
                         cluster_cmp.name if hasattr(cluster_cmp, "name")
                         else cluster_cmp["name"],
                         "Invalid cluster name value")
        self.assertEqual(cluster_ref.status if hasattr(cluster_ref, "status")
                         else cluster_ref["status"],
                         cluster_cmp.status if hasattr(cluster_cmp, "status")
                         else cluster_cmp["status"],
                         "Invalid cluster status value")
        self.assertEqual(cluster_ref.flavor if hasattr(cluster_ref, "flavor")
                         else cluster_ref["flavor"],
                         cluster_cmp.flavor if hasattr(cluster_cmp, "flavor")
                         else cluster_cmp["flavor"],
                         "Invalid cluster flavor value")
        self.assertEqual(cluster_ref.size if hasattr(cluster_ref, "size")
                         else cluster_ref["size"],
                         cluster_cmp.size if hasattr(cluster_cmp, "size")
                         else cluster_cmp["size"],
                         "Invalid cluster size value")
        self.assertEqual(cluster_ref.volume_size if hasattr(cluster_ref,
                                                            "volume_size")
                         else cluster_ref["volume_size"],
                         cluster_cmp.volume_size if hasattr(cluster_cmp,
                                                            "volume_size")
                         else cluster_cmp["volume_size"],
                         "Invalid cluster volume_size value")
        self.assertTrue(compare_dates(
                        cluster_ref.created_at if hasattr(cluster_ref,
                                                          "created_at")
                        else cluster_ref["created_at"],
                        cluster_cmp.created_at if hasattr(cluster_cmp,
                                                          "created_at")
                        else cluster_cmp["created_at"]),
                        "Invalid created_at value")

        self.assertTrue(compare_dates(
                        cluster_ref.updated_at if hasattr(cluster_ref,
                                                          "updated_at")
                        else cluster_ref["updated_at"],
                        cluster_cmp.updated_at if hasattr(cluster_cmp,
                                                          "updated_at")
                        else cluster_cmp["updated_at"]),
                        "Invalid updated_at value")

        if not isinstance((cluster_ref.network_id if hasattr(cluster_ref,
                                                             "network_id")
                           else cluster_ref["network_id"]), (str, unicode)):
            cluster_ref['network_id'] = cluster_ref['network_id'][0]

        if not isinstance((cluster_cmp.network_id if hasattr(cluster_cmp,
                                                             "network_id")
                           else cluster_cmp["network_id"]), (str, unicode)):
            cluster_cmp['network_id'] = cluster_cmp['network_id'][0]

        self.assertEqual(cluster_ref.network_id if hasattr(cluster_ref,
                                                           "network_id")
                         else cluster_ref["network_id"],
                         cluster_cmp.network_id if hasattr(cluster_cmp,
                                                           "network_id")
                         else cluster_cmp["network_id"],
                         "Invalid cluster network_id value")
