# -*- encoding: utf-8 -*-
#
# Copyright © 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

import pecan
from pecan import rest
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

from cue.api.controllers import base
from cue.api.controllers import link
from cue.api.controllers import v1


class Version(base.APIBase):
    """An API version representation."""

    id = wtypes.text
    "The ID of the version, also acts as the release number"

    links = [link.Link]
    "A Link that point to a specific version of the API"

    status = wtypes.text
    "The status of this version"

    @classmethod
    def convert(self, id, status):
        version = Version()
        version.id = id
        version.status = status
        version.links = [link.Link.make_link('self', pecan.request.host_url,
                                             id, '', bookmark=True)]
        return version


class Root(base.APIBase):

    name = wtypes.text
    "The name of the API"

    description = wtypes.text
    "Some information about this API"

    versions = [Version]
    "Links to all the versions available in this API"

    default_version = Version
    "A link to the default version of the API"

    @classmethod
    def convert(self):
        """Builds link to v1 controller."""
        root = Root()
        root.name = "OpenStack Cue API"
        root.description = ("Cue is an OpenStack project which aims to "
                            "provision Messaging Brokers.")
        root.versions = [Version.convert('v1', 'STABLE')]
        root.default_version = Version.convert('v1', 'STABLE')
        return root


class RootController(rest.RestController):

    _versions = ['v1']
    "All supported API versions"

    _default_version = 'v1'
    "The default API version"

    v1 = v1.V1Controller()

    @wsme_pecan.wsexpose(Root)
    def get(self):
        # NOTE: The reason why convert() it's being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return Root.convert()

    @pecan.expose()
    def _route(self, args):
        """Overrides the default routing behavior.

        It redirects the request to the default version of the cue API
        if the version number is not specified in the url.
        """

        if args[0] and args[0] not in self._versions:
            args = [self._default_version] + args
        return super(RootController, self)._route(args)
