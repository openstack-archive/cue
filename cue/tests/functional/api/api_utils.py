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


class ClusterValidationMixin(object):
    cluster_name = "test-cluster"

    def validate_cluster_values(self, cluster_ref, cluster_cmp):
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
        self.assertEqual(unicode(cluster_ref["created_at"].isoformat()),
                         cluster_cmp["created_at"],
                         "Invalid cluster created_at value")

        if cluster_ref["updated_at"] is not None:
            self.assertEqual(unicode(cluster_ref["updated_at"].isoformat()),
                             cluster_cmp["updated_at"],
                             "Invalid cluster updated_at value")

        if isinstance((cluster_ref.network_id if hasattr(cluster_ref,
                                                           "network_id")
                         else cluster_ref["network_id"]), (str, unicode)):
            cluster_ref['network_id'] = [cluster_ref['network_id']]

        if isinstance((cluster_cmp.network_id if hasattr(cluster_cmp,
                                                           "network_id")
                         else cluster_cmp["network_id"]), (str, unicode)):
            cluster_cmp['network_id'] = [cluster_cmp['network_id']]

        self.assertEqual(len(cluster_ref.network_id if hasattr(cluster_ref,
                                                           "network_id")
                         else cluster_ref["network_id"]),
                         len(cluster_cmp.network_id if hasattr(cluster_cmp,
                                                           "network_id")
                         else cluster_cmp["network_id"]),
                         "Unequal number of cluster network_id")

        for i, network_id in enumerate(cluster_ref.network_id if hasattr(
                cluster_ref, "network_id") else cluster_ref["network_id"]):
            self.assertEqual(network_id, cluster_cmp.network_id[i] if hasattr(
                cluster_cmp, "network_id") else cluster_cmp["network_id"][i],
                             "Invalid cluster network_id value")

    def validate_endpoint_values(self, endpoints_ref, endpoints_cmp):
        self.assertEqual(len(endpoints_ref), len(endpoints_cmp),
                         "Invalid number of endpoints")

        sorted_endpoints_ref = sorted(endpoints_ref, key=lambda k: k['uri'])
        sorted_endpoints_cmp = sorted(endpoints_cmp, key=lambda k: k['uri'])

        for endpoint_ref, endpoint_cmp in zip(sorted_endpoints_ref,
                                              sorted_endpoints_cmp):
            self.assertEqual(endpoint_ref['uri'], endpoint_cmp['uri'],
                             'Invalid endpoint uri')
            self.assertEqual(endpoint_ref['type'], endpoint_cmp['type'],
                             'Invalid endpoint type')
