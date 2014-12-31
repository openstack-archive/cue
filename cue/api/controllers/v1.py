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
from cue.api.controllers import base
from cue import objects

import uuid

import pecan
from pecan import rest
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan


class EndPoint(base.APIBase):
    """Representation of an End point."""

    def __init__(self, **kwargs):
        self.fields = []
        endpoint_object_fields = list(objects.Endpoint.fields)
        for k in endpoint_object_fields:
            # only add fields we expose in the api
            if hasattr(self, k):
                self.fields.append(k)
                setattr(self, k, kwargs.get(k, wtypes.Unset))

    type = wtypes.text
    "type of endpoint"

    uri = wtypes.text
    "URL to endpoint"


class Cluster(base.APIBase):
    """Representation of a cluster."""

    def __init__(self, **kwargs):
        self.fields = []
        cluster_object_fields = list(objects.Cluster.fields)
        # Adding nodes since it is an api-only attribute.
        self.fields.append('nodes')
        for k in cluster_object_fields:
            # only add fields we expose in the api
            if hasattr(self, k):
                self.fields.append(k)
                setattr(self, k, kwargs.get(k, wtypes.Unset))

    id = wtypes.text
    "UUID of cluster"

    network_id = wtypes.wsattr(wtypes.text, mandatory=True)
    "NIC of Neutron network"

    name = wsme.wsattr(wtypes.text, mandatory=True)
    "Name of cluster"

    status = wtypes.text
    "Current status of cluster"

    flavor = wsme.wsattr(wtypes.text, mandatory=True)
    "Flavor of cluster"

    size = wtypes.IntegerType()
    "Number of nodes in cluster"

    volume_size = wtypes.IntegerType()
    "Volume size for nodes in cluster"

    end_points = wtypes.wsattr([EndPoint], default=[])
    "List of endpoints on accessing node"


def get_complete_cluster(cluster_id):
    """Helper to retrieve the api-compatible full structure of a cluster."""

    cluster_obj = objects.Cluster.get_cluster_by_id(cluster_id)

    # construct api cluster object
    cluster = Cluster(**cluster_obj.as_dict())

    cluster_nodes = objects.Node.get_nodes_by_cluster_id(cluster_id)

    for node in cluster_nodes:
        # extract endpoints from node
        node_endpoints = objects.Endpoint.get_endpoints_by_node_id(node.id)

        # construct api endpoint objects
        cluster.end_points = [EndPoint(**obj_endpoint.as_dict()) for
                              obj_endpoint in node_endpoints]

    return cluster


class ClusterController(rest.RestController):
    """Manages operations on specific Cluster of nodes."""

    def __init__(self, cluster_id):
        self.id = cluster_id

    @wsme_pecan.wsexpose(Cluster, status_code=200)
    def get(self):
        """Return this cluster."""

        cluster = get_complete_cluster(self.id)

        return cluster

    @wsme_pecan.wsexpose(None, status_code=202)
    def delete(self):
        """Delete this Cluster."""
        objects.Cluster.mark_cluster_as_delete(self.id)


class ClustersController(rest.RestController):
    """Manages operations on Clusters of nodes."""

    @wsme_pecan.wsexpose([Cluster], status_code=200)
    def get(self):
        """Return list of Clusters."""
        # TODO(dagnello): update project_id accordingly when enabled
        clusters = objects.Cluster.get_clusters(project_id=0)
        cluster_list = [Cluster(**obj_cluster.as_dict()) for obj_cluster in
                        clusters]

        return cluster_list

    @wsme_pecan.wsexpose(Cluster, body=Cluster, status_code=202)
    def post(self, data):
        """Create a new Cluster.

        :param data: cluster parameters within the request body.
        """

        # create new cluster object with required data from user
        new_cluster = objects.Cluster(**data.as_dict())

        # TODO(dagnello): project_id will have to be extracted from HTTP header
        project_id = unicode(uuid.uuid1())

        # create new cluster with node related data from user
        new_cluster.create_cluster(project_id)

        cluster = get_complete_cluster(new_cluster.id)

        return cluster

    @pecan.expose()
    def _lookup(self, cluster_id, *remainder):
        return ClusterController(cluster_id), remainder


class V1Controller(object):
    """Version 1 MSGaaS API controller root."""
    clusters = ClustersController()