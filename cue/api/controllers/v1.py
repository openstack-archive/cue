# Copyright 2014 Hewlett-Packard Development Company, L.P.
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

"""Version 1 of the Cue API
"""
import datetime

import pecan
from pecan import rest
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan


class EndPoint():
    type = wtypes.text
    "type of endpoint"

    value = wtypes.text
    "URL to endpoint"


class Node():
    """Representation of a Node."""

    node_id = wtypes.text
    "UUID of node"

    flavor = wsme.wsattr(wtypes.text, mandatory=True)
    "Flavor of cluster"

    status = wtypes.text
    "Current status of node"

    end_points = wtypes.wsattr([EndPoint], default=[])
    "List of endpoints on accessing node"

    created = datetime.datetime
    "Creation of node date-time"

    updated = datetime.datetime
    "Last update of node date-time"


class Cluster():
    """Representation of a cluster."""

    cluster_id = wtypes.text
    "UUID of cluster"

    nic = wtypes.wsattr(wtypes.text, mandatory=True)
    "NIC of Neutron network"

    nodes = wtypes.wsattr([Node], default=[])
    "List of nodes of cluster"

    name = wsme.wsattr(wtypes.text, mandatory=True)
    "Name of cluster"

    status = wtypes.text
    "Current status of cluster"

    volume_size = wtypes.IntegerType()
    "Volume size for nodes in cluster"

    created = datetime.datetime
    "Creation of cluster date-time"

    updated = datetime.datetime
    "Last update of cluster date-time"


class ClusterController(rest.RestController):
    """Manages operations on specific Cluster of nodes."""

    def __init__(self, cluster_id):
        self.cluster_id = cluster_id

    @wsme_pecan.wsexpose(Cluster, status_code=200)
    def get(self):
        """Return this cluster."""
        cluster = Cluster()

        return cluster

    @wsme_pecan.wsexpose(None, status_code=202)
    def delete(self):
        """Delete this Cluster."""
        cluster = Cluster()
        cluster.cluster_id = self.cluster_id


class ClustersController(rest.RestController):
    """Manages operations on Clusters of nodes."""

    @wsme_pecan.wsexpose([Cluster], status_code=200)
    def get(self):
        """Return list of Clusters."""
        cluster_list = []

        return cluster_list

    @wsme_pecan.wsexpose(Cluster, body=Cluster, status_code=202)
    def post(self, data):
        """Create a new Cluster.

        :param data: cluster parameters within the request body.
        """

        cluster_flavor = data.nodes[0].flavor
        for node in data.nodes:
            # nodes of different flavors in same cluster are not supported
            if cluster_flavor != node.flavor:
                pecan.abort(400)

        return data

    @pecan.expose()
    def _lookup(self, cluster_id, *remainder):
        return ClusterController(cluster_id), remainder


class V1Controller(object):
    """Version 1 MSGaaS API controller root."""
    clusters = ClustersController()