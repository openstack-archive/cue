# Copyright [2014] Hewlett-Packard Development Company, L.P.
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
Initial submission sets up the REST routes using Pecan framework.  Some
temporary sample code has been added to functions.  This sample code will be
removed and replaced with the intended implementation in future submissions.
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

    nodes = wtypes.wsattr([Node], default=[])
    "List of nodes of cluster"

    name = wsme.wsattr(wtypes.text, mandatory=True)
    "Name of cluster"

    status = wtypes.text
    "Current status of cluster"

    created = datetime.datetime
    "Creation of cluster date-time"

    updated = datetime.datetime
    "Last update of cluster date-time"


class NodeController(rest.RestController):
    """Manages operations on specific node within a Cluster."""

    def __init__(self, cluster_id, node_id):
        self.cluster_id = cluster_id
        self.node_id = node_id

    @wsme_pecan.wsexpose(Node, status_code=200)
    def get(self):
        """Return this node."""
        node = Node()
        node.node_id = self.node_id
        node.status = 'ACTIVE'
        node.flavor = 'medium'
        node.created = datetime.datetime.utcnow()
        node.updated = datetime.datetime.utcnow()
        end_point = EndPoint()
        end_point.type = 'AMQP'
        end_point.value = 'amqp://10.20.30.40:5672'
        node.end_points.append(end_point)
        end_point = EndPoint()
        end_point.type = 'console'
        end_point.value = 'http://10.20.30.40:10000'
        node.end_points.append(end_point)
        return node

    @wsme_pecan.wsexpose(None, status_code=202)
    def delete(self):
        """Delete this Node."""
        node = Node()
        node.node_id = self.node_id


class NodesController(rest.RestController):
    """Manages operations on nodes within a Cluster."""

    def __init__(self, cluster_id):
        self.cluster_id = cluster_id

    @wsme_pecan.wsexpose(Cluster, status_code=200)
    def get(self):
        """Return set of Nodes in Cluster."""
        cluster = Cluster()
        cluster.cluster_id = self.cluster_id
        cluster.name = 'cluster 1'
        cluster.created = datetime.datetime.utcnow()
        cluster.updated = datetime.datetime.utcnow()
        cluster.status = 'ACTIVE'

        node = Node()
        node.node_id = '616fb98f-46ca-475e-917e-2563e5a8cd19'
        node.status = 'ACTIVE'
        node.flavor = 'medium'
        node.created = datetime.datetime.utcnow()
        node.updated = datetime.datetime.utcnow()
        end_point = EndPoint()
        end_point.type = 'AMQP'
        end_point.value = 'amqp://10.20.30.40:5672'
        node.end_points.append(end_point)
        end_point = EndPoint()
        end_point.type = 'console'
        end_point.value = 'http://10.20.30.40:10000'
        node.end_points.append(end_point)

        cluster.nodes.append(node)

        node = Node()
        node.node_id = 'e90c9d13-c4b8-4a08-992a-dad6109b8ac2'
        node.status = 'ACTIVE'
        node.flavor = 'medium'
        node.created = datetime.datetime.utcnow()
        node.updated = datetime.datetime.utcnow()
        end_point = EndPoint()
        end_point.type = 'AMQP'
        end_point.value = 'amqp://10.20.30.41:5672'
        node.end_points.append(end_point)
        end_point = EndPoint()
        end_point.type = 'console'
        end_point.value = 'http://10.20.30.41:10000'
        node.end_points.append(end_point)

        cluster.nodes.append(node)

        node = Node()
        node.node_id = '372f8f47-6818-4d83-aa42-8744c0e689b8'
        node.status = 'ACTIVE'
        node.flavor = 'medium'
        node.created = datetime.datetime.utcnow()
        node.updated = datetime.datetime.utcnow()
        end_point = EndPoint()
        end_point.type = 'AMQP'
        end_point.value = 'amqp://10.20.30.42:5672'
        node.end_points.append(end_point)
        end_point = EndPoint()
        end_point.type = 'console'
        end_point.value = 'http://10.20.30.42:10000'
        node.end_points.append(end_point)

        cluster.nodes.append(node)
        return cluster

    @wsme_pecan.wsexpose(Node, status_code=202)
    def post(self):
        """Create new Node."""
        node = Node()
        node.node_id = self.node_id
        node.status = 'BUILDING'
        node.flavor = 'medium'
        node.created = datetime.datetime.utcnow()
        node.updated = datetime.datetime.utcnow()
        end_point = EndPoint()
        end_point.type = 'AMQP'
        end_point.value = 'amqp://10.20.30.40:5672'
        node.end_points.append(end_point)
        end_point = EndPoint()
        end_point.type = 'console'
        end_point.value = 'http://10.20.30.40:10000'
        node.end_points.append(end_point)
        return node

    @pecan.expose()
    def _lookup(self, node_id, *remainder):
        return NodeController(self.cluster_id, node_id), remainder


class ClusterController(rest.RestController):
    """Manages operations on specific Cluster of nodes."""

    def __init__(self, cluster_id):
        self.cluster_id = cluster_id

    @wsme_pecan.wsexpose(Cluster, status_code=200)
    def get(self):
        """Return this cluster."""
        cluster = Cluster()
        cluster.cluster_id = self.cluster_id
        cluster.name = 'cluster 1'
        cluster.created = datetime.datetime.utcnow()
        cluster.updated = datetime.datetime.utcnow()
        cluster.status = 'ACTIVE'

        node = Node()
        node.node_id = '616fb98f-46ca-475e-917e-2563e5a8cd19'
        node.status = 'ACTIVE'
        node.flavor = 'medium'
        node.created = datetime.datetime.utcnow()
        node.updated = datetime.datetime.utcnow()
        end_point = EndPoint()
        end_point.type = 'AMQP'
        end_point.value = 'amqp://10.20.30.40:5672'
        node.end_points.append(end_point)
        end_point = EndPoint()
        end_point.type = 'console'
        end_point.value = 'http://10.20.30.40:10000'
        node.end_points.append(end_point)

        cluster.nodes.append(node)

        node = Node()
        node.node_id = 'e90c9d13-c4b8-4a08-992a-dad6109b8ac2'
        node.status = 'ACTIVE'
        node.flavor = 'medium'
        node.created = datetime.datetime.utcnow()
        node.updated = datetime.datetime.utcnow()
        end_point = EndPoint()
        end_point.type = 'AMQP'
        end_point.value = 'amqp://10.20.30.41:5672'
        node.end_points.append(end_point)
        end_point = EndPoint()
        end_point.type = 'console'
        end_point.value = 'http://10.20.30.41:10000'
        node.end_points.append(end_point)

        cluster.nodes.append(node)

        node = Node()
        node.node_id = '372f8f47-6818-4d83-aa42-8744c0e689b8'
        node.status = 'ACTIVE'
        node.flavor = 'medium'
        node.created = datetime.datetime.utcnow()
        node.updated = datetime.datetime.utcnow()
        end_point = EndPoint()
        end_point.type = 'AMQP'
        end_point.value = 'amqp://10.20.30.42:5672'
        node.end_points.append(end_point)
        end_point = EndPoint()
        end_point.type = 'console'
        end_point.value = 'http://10.20.30.42:10000'
        node.end_points.append(end_point)

        cluster.nodes.append(node)

        return cluster

    @wsme_pecan.wsexpose(None, status_code=202)
    def delete(self):
        """Delete this Cluster."""
        cluster = Cluster()
        cluster.cluster_id = self.cluster_id

    @pecan.expose()
    def _lookup(self, resource, *remainder):
        if resource == 'nodes':
            return NodesController(self.cluster_id), remainder
        else:
            pecan.abort(404)


class ClustersController(rest.RestController):
    """Manages operations on Clusters of nodes."""

    @wsme_pecan.wsexpose([Cluster], status_code=200)
    def get(self):
        """Return list of Clusters."""
        cluster_list = []
        cluster = Cluster()
        cluster.cluster_id = 'dd745f4a-9333-417e-bb89-9c989c84c068'
        cluster.name = 'cluster 1'
        cluster.created = datetime.datetime.utcnow()
        cluster.updated = datetime.datetime.utcnow()
        cluster.status = 'ACTIVE'

        cluster_list.append(cluster)
        cluster = Cluster()
        cluster.cluster_id = '3caa8fe3-a760-4f83-8bb6-6d70c786f339'
        cluster.name = 'cluster 2'
        cluster.created = datetime.datetime.utcnow()
        cluster.updated = datetime.datetime.utcnow()
        cluster.status = 'ACTIVE'
        cluster_list.append(cluster)
        return cluster_list

    @wsme_pecan.wsexpose(Cluster, status_code=202)
    def post(self):
        """Create a new Cluster."""
        cluster = Cluster()
        cluster.cluster_id = 'dd745f4a-9333-417e-bb89-9c989c84c068'
        cluster.name = 'cluster 1'
        cluster.created = datetime.datetime.utcnow()
        cluster.updated = datetime.datetime.utcnow()
        cluster.status = 'ACTIVE'

        node = Node()
        node.node_id = '616fb98f-46ca-475e-917e-2563e5a8cd19'
        node.status = 'ACTIVE'
        node.flavor = 'medium'
        node.created = datetime.datetime.utcnow()
        node.updated = datetime.datetime.utcnow()
        end_point = EndPoint()
        end_point.type = 'AMQP'
        end_point.value = 'amqp://10.20.30.40:5672'
        node.end_points.append(end_point)
        end_point = EndPoint()
        end_point.type = 'console'
        end_point.value = 'http://10.20.30.40:10000'
        node.end_points.append(end_point)

        cluster.nodes.append(node)

        node = Node()
        node.node_id = 'e90c9d13-c4b8-4a08-992a-dad6109b8ac2'
        node.status = 'ACTIVE'
        node.flavor = 'medium'
        node.created = datetime.datetime.utcnow()
        node.updated = datetime.datetime.utcnow()
        end_point = EndPoint()
        end_point.type = 'AMQP'
        end_point.value = 'amqp://10.20.30.41:5672'
        node.end_points.append(end_point)
        end_point = EndPoint()
        end_point.type = 'console'
        end_point.value = 'http://10.20.30.41:10000'
        node.end_points.append(end_point)

        cluster.nodes.append(node)

        node = Node()
        node.node_id = '372f8f47-6818-4d83-aa42-8744c0e689b8'
        node.status = 'ACTIVE'
        node.flavor = 'medium'
        node.created = datetime.datetime.utcnow()
        node.updated = datetime.datetime.utcnow()
        end_point = EndPoint()
        end_point.type = 'AMQP'
        end_point.value = 'amqp://10.20.30.42:5672'
        node.end_points.append(end_point)
        end_point = EndPoint()
        end_point.type = 'console'
        end_point.value = 'http://10.20.30.42:10000'
        node.end_points.append(end_point)

        cluster.nodes.append(node)
        return cluster

    @pecan.expose()
    def _lookup(self, cluster_id, *remainder):
        return ClusterController(cluster_id), remainder


class V1Controller(object):
    """Version 1 MSGaaS API controller root."""
    clusters = ClustersController()