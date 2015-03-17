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
from cue.common import exception
from cue.common.i18n import _  # noqa
from cue.common.i18n import _LI  # noqa
from cue import objects
from cue.taskflow import client as task_flow_client
from cue.taskflow.flow import create_cluster
from cue.taskflow.flow import delete_cluster

from oslo.config import cfg
from oslo.utils import uuidutils
from oslo_log import log as logging
import pecan
from pecan import rest
import wsme
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


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


class ClusterDetails(base.APIBase):
    """Representation of a cluster's details."""
    # todo(dagnello): WSME attribute verification sometimes triggers 500 server
    # error when user input was actually invalid (400).  Example: if 'size' was
    # provided as a string/char, e.g. 'a', api returns 500 server error.

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

    size = wsme.wsattr(wtypes.IntegerType(), mandatory=True)
    "Number of nodes in cluster"

    volume_size = wtypes.IntegerType()
    "Volume size for nodes in cluster"

    end_points = wtypes.wsattr([EndPoint], default=[])
    "List of endpoints on accessing node"


class Cluster(base.APIBase):
    """API representation of a cluster."""

    cluster = ClusterDetails

    def __init__(self, **kwargs):
        self._type = 'cluster'


class ClusterCollection(base.APIBase):
    """API representation of a collection of clusters."""

    clusters = [ClusterDetails]
    """A list containing Cluster objects"""

    def __init__(self, **kwargs):
        self._type = 'clusters'


def get_complete_cluster(context, cluster_id):
    """Helper to retrieve the api-compatible full structure of a cluster."""

    cluster_obj = objects.Cluster.get_cluster_by_id(context, cluster_id)

    # construct api cluster object
    cluster = ClusterDetails(**cluster_obj.as_dict())
    cluster.end_points = []

    cluster_nodes = objects.Node.get_nodes_by_cluster_id(context, cluster_id)

    for node in cluster_nodes:
        # extract endpoints from node
        node_endpoints = objects.Endpoint.get_endpoints_by_node_id(context,
                                                                   node.id)

        # construct api endpoint objects
        node_endpoints_dict = [EndPoint(**obj_endpoint.as_dict()) for
                               obj_endpoint in node_endpoints]

        cluster.end_points.extend(node_endpoints_dict)

    return cluster


class ClusterController(rest.RestController):
    """Manages operations on specific Cluster of nodes."""

    @wsme_pecan.wsexpose(Cluster, wtypes.text, status_code=200)
    def get_one(self, cluster_id):
        """Return this cluster."""
        context = pecan.request.context
        cluster = Cluster()
        cluster.cluster = get_complete_cluster(context, cluster_id)

        return cluster

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=202)
    def delete(self, cluster_id):
        """Delete this Cluster."""
        context = pecan.request.context

        # update cluster to deleting
        objects.Cluster.update_cluster_deleting(context, cluster_id)

        # retrieve cluster nodes
        nodes = objects.Node.get_nodes_by_cluster_id(context, cluster_id)

        # create list with node id's for create cluster flow
        node_ids = [node.id for node in nodes]

        # prepare and post cluster delete job to backend
        flow_kwargs = {
            'cluster_id': cluster_id,
            'node_ids': node_ids,
        }

        job_args = {
            "context": context.to_dict(),
        }

        job_client = task_flow_client.get_client_instance()
        #TODO(dagnello): might be better to use request_id for job_uuid
        job_uuid = uuidutils.generate_uuid()
        job_client.post(delete_cluster, job_args, flow_kwargs=flow_kwargs,
                        tx_uuid=job_uuid)

        LOG.info(_LI('Delete Cluster Request Cluster ID %(cluster_id)s Job ID '
                     '%(job_id)s') % ({"cluster_id": cluster_id,
                                       "job_id": job_uuid}))

    @wsme_pecan.wsexpose(ClusterCollection, status_code=200)
    def get_all(self):
        """Return list of Clusters."""

        context = pecan.request.context
        clusters = objects.Cluster.get_clusters(context)
        cluster_list = ClusterCollection()
        cluster_list.clusters = [get_complete_cluster(context, obj_cluster.id)
                                 for obj_cluster in clusters]

        return cluster_list

    @wsme_pecan.wsexpose(Cluster, body=ClusterDetails,
                         status_code=202)
    def post(self, data):
        """Create a new Cluster.

        :param data: cluster parameters within the request body.
        """
        context = pecan.request.context

        if data.size <= 0:
            raise exception.Invalid(_("Invalid cluster size provided"))

        # create new cluster object with required data from user
        new_cluster = objects.Cluster(**data.as_dict())

        # create new cluster with node related data from user
        new_cluster.create(context)

        # retrieve cluster data
        cluster = Cluster()
        cluster.cluster = get_complete_cluster(context, new_cluster.id)

        nodes = objects.Node.get_nodes_by_cluster_id(context,
                                                     cluster.cluster.id)

        # create list with node id's for create cluster flow
        node_ids = [node.id for node in nodes]

        # prepare and post cluster create job to backend
        flow_kwargs = {
            'cluster_id': cluster.cluster.id,
            'node_ids': node_ids,
            'user_network_id': cluster.cluster.network_id,
            'management_network_id': CONF.management_network_id,
        }

        # generate unique erlang cookie to be used by all nodes in the new
        # cluster, erlang cookies are strings of up to 255 characters
        erlang_cookie = uuidutils.generate_uuid()
        default_rabbit_user = 'rabbitmq'
        default_rabbit_pass = cluster.cluster.id

        job_args = {
            'flavor': cluster.cluster.flavor,
            # TODO(sputnik13): need to remove this when image selector is done
            'image': CONF.api.os_image_id,
            'volume_size': cluster.cluster.volume_size,
            'context': context.to_dict(),
            # TODO(sputnik13: this needs to come from the create request and
            # default to a configuration value rather than always using config
            # value
            'security_groups': [CONF.os_security_group],
            'port': CONF.rabbit_port,
            'key_name': CONF.openstack.os_key_name,
            'erlang_cookie': erlang_cookie,
            'default_rabbit_user': default_rabbit_user,
            'default_rabbit_pass': default_rabbit_pass,
        }
        job_client = task_flow_client.get_client_instance()
        #TODO(dagnello): might be better to use request_id for job_uuid
        job_uuid = uuidutils.generate_uuid()
        job_client.post(create_cluster, job_args,
                        flow_kwargs=flow_kwargs,
                        tx_uuid=job_uuid)

        LOG.info(_LI('Create Cluster Request Cluster ID %(cluster_id)s Cluster'
                     ' size %(size)s network ID %(network_id)s Job ID '
                     '%(job_id)s') % ({"cluster_id": cluster.cluster.id,
                                       "size": cluster.cluster.size,
                                       "network_id":
                                           cluster.cluster.network_id,
                                       "job_id": job_uuid}))

        cluster.cluster.additional_information = []
        cluster.cluster.additional_information.append(
            dict(def_rabbit_user=default_rabbit_user))
        cluster.cluster.additional_information.append(
            dict(def_rabbit_pass=default_rabbit_pass))

        return cluster
