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

"""
Version 1 of the Cue API

"""

import pecan
from pecan import rest
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from cue.api.controllers import base
from cue.api.controllers import link
from cue.api.controllers.v1 import cluster


class V1(base.APIBase):
    """The representation of the version 1 of the API."""

    id = wtypes.text
    """The ID of the version, also acts as the release number"""

    status = wtypes.text
    """The status of this version"""

    clusters = [link.Link]
    """Links to the cluster resource"""

    @staticmethod
    def convert():
        """Builds link to clusters controller."""
        v1 = V1()
        v1.id = "v1"
        v1.status = "Stable"

        v1.clusters = [link.Link.make_link('self', pecan.request.host_url,
                                           'clusters', ''),
                       link.Link.make_link('bookmark',
                                           pecan.request.host_url, v1.id,
                                           'clusters',
                                           bookmark=True)
                       ]
        return v1


class V1Controller(rest.RestController):
    """Version 1 MSGaaS API controller root."""

    _versions = ['v1']
    "All supported API versions"

    _default_version = 'v1'
    "The default API version"
    clusters = cluster.ClustersController()

    @wsme_pecan.wsexpose(V1)
    def get(self):
        # NOTE: The reason why convert() it's being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return V1.convert()

    @pecan.expose()
    def _route(self, args):
        return super(V1Controller, self)._route(args)