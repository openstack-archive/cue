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

import os

from cueclient.v1 import client
import keystoneclient
from rally.benchmark.scenarios import base

auth = keystoneclient.auth.identity.v2.Password(
    auth_url=os.environ['OS_AUTH_URL'],
    username=os.environ['OS_USERNAME'],
    password=os.environ['OS_PASSWORD'],
    tenant_name=os.environ['OS_TENANT_NAME']
 )


class CueScenarioPlugin(base.Scenario):
    """Plugin which lists instances."""

    @base.scenario()
    def list_clusters(self):
        """test description."""
        session = keystoneclient.session.Session(auth=auth)
        cue_client = client.Client(session=session)
        custom_data = cue_client.clusters.list()
        assert custom_data == []

    @base.scenario()
    def list_clusters2(self):
        """test description 2."""
        session = keystoneclient.session.Session(auth=auth)
        cue_client = client.Client(session=session)
        custom_data = cue_client.clusters.list()
        assert custom_data != []
