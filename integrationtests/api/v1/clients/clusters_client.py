# Copyright 2014 OpenStack Foundation
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

import json
import logging
import urllib

from tempest_lib.common import rest_client

from integrationtests.common.client import BaseMessageQueueClient

LOG = logging.getLogger(__name__)


class MessageQueueClustersClient(BaseMessageQueueClient):

    def list_clusters(self, params=None):
        url = 'clusters'
        if params:
            url += '?%s' % urllib.urlencode(params)

        resp, body = self.get(url)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBodyData(resp, body)

    def get_cluster_details(self, cluster_id):
        resp, body = self.get("clusters/%s" % str(cluster_id))
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, self._parse_resp(body))

    def create_cluster(self, name, flavor, network_id):
        post_body = {
            'name': name,
            'size': 1,
            "flavor": flavor,
            'volume_size': 100,
            "network_id": network_id,
        }

        post_body = post_body
        post_body = json.dumps(post_body)

        resp, body = self.post('clusters', post_body)
        return rest_client.ResponseBody(resp, self._parse_resp(body))

    def delete_cluster(self, cluster_id):
        resp, body = self.delete("clusters/%s" % str(cluster_id))
        self.expected_success(202, resp.status)
        return rest_client.ResponseBody(resp, body)