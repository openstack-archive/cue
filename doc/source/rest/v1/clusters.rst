..
    Copyright 2015 Hewlett-Packard Development Company, L.P.

    Licensed under the Apache License, Version 2.0 (the "License"); you may
    not use this file except in compliance with the License. You may obtain
    a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.


========
Clusters
========

A Cluster is a representation of a collection of message broker nodes with
respective endpoints (e.g. RabbitMQ Cluster).


Create Cluster
==============

.. http:post:: /clusters

  Create a new Cluster.

  **Example request**:

  .. code-block:: http

     POST /clusters HTTP/1.1
     Host: example.com
     Accept: application/json
     Content-Type: application/json

     {
        "name": "Example Cluster",
        "size": 3,
        "flavor": "101",
        "volume_size": "1048576"
        "network_id": [
            "ea540512-4d4a-4c46-9ebd-4fafe4a54a2d"
        ]
     }


  **Example response**:

  .. code-block:: http

    HTTP/1.1 201 Created
    Location: http://127.0.0.1:8795/v1/clusters/2c3c66ba-721b-4443-bc81-55d986848c68
    Content-Type: application/json; charset=UTF-8

    {
        "status": "BUILDING",
        "name": "Example Cluster",
        "network_id": [
            "ea540512-4d4a-4c46-9ebd-4fafe4a54a2d"
        ],
        "created_at": "2015-06-03T21:49:49+00:00",
        "volume_size": 1048576,
        "end_points": [],
        "flavor": "101",
        "id": "2c3c66ba-721b-4443-bc81-55d986848c68",
        "size": 3
    }

  :form status: status of the cluster
  :form name: name of the cluster
  :form network_id: a list of UUID of network id's
  :form created_at: create cluster request received timestamp
  :form volume_size: volume size used for each node
  :form end_points: list of endpoints for each node
  :form flavor: node flavor
  :form id: the UUID of the cluster
  :form size: size of the cluster

  :statuscode 201: Created
  :statuscode 400: Bad Request
  :statuscode 401: Access Denied


Get Cluster
===========

.. http:get:: /clusters/(uuid:id)

  Get a specific Cluster using the Cluster's uuid id.

  **Example request**:

  .. code-block:: http

    GET /clusters/2c3c66ba-721b-4443-bc81-55d986848c68 HTTP/1.1
    Host: example.com
    Accept: application/json

  **Example response**:

  .. code-block:: http

    HTTP/1.1 200 OK
    Content-Type: application/json; charset=UTF-8

    {
        "status": "ACTIVE",
        "name": "Example Cluster",
        "network_id": [
            "c6958944-7ef0-4929-9625-7f924bb2610c"
        ],
        "created_at": "2015-06-03T22:44:17+00:00",
        "updated_at": "2015-06-03T22:47:15+00:00",
        "volume_size": 1048576,
        "end_points": [
            {
                "type": "AMQP",
                "uri": "10.0.0.9:5672"
            },
            {
                "type": "AMQP",
                "uri": "10.0.0.11:5672"
            },
            {
                "type": "AMQP",
                "uri": "10.0.0.10:5672"
            }
        ],
        "flavor": "8795",
        "id": "2c3c66ba-721b-4443-bc81-55d986848c68",
        "size": 3
    }

  :form updated_at: cluster last updated at timestamp

  :statuscode 200: OK
  :statuscode 400: Bad Request

List Clusters
=============

.. http:get:: /clusters

   Lists all clusters

   **Example request**:

   .. sourcecode:: http

      GET /servers HTTP/1.1
      Host: example.com
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json

      {
        "status": "ACTIVE",
        "name": "Example Cluster",
        "network_id": [
            "c6958944-7ef0-4929-9625-7f924bb2610c"
        ],
        "created_at": "2015-06-03T22:44:17+00:00",
        "updated_at": "2015-06-04T00:31:16+00:00",
        "volume_size": 1048576,
        "end_points": [
            {
                "type": "AMQP",
                "uri": "10.0.0.9:5672"
            },
            {
                "type": "AMQP",
                "uri": "10.0.0.11:5672"
            },
            {
                "type": "AMQP",
                "uri": "10.0.0.10:5672"
            }
        ],
        "flavor": "8795",
        "id": "2c3c66ba-721b-4443-bc81-55d986848c68",
        "size": 3
    },
    {
        "status": "DELETED",
        "name": "cluster_01",
        "network_id": [
            "ba013641-8b54-40a5-801d-a7839690e272"
        ],
        "created_at": "2015-05-13T21:23:15+00:00",
        "updated_at": "2015-05-13T21:30:15+00:00",
        "end_points": [
            {
                "type": "AMQP",
                "uri": "10.0.0.7:5672"
            }
        ],
        "flavor": "8795",
        "id": "85a63cac-9bf7-4ef7-962d-dd51bde0b29b",
        "size": 1
    },

   :statuscode 200: Success
   :statuscode 401: Access Denied



Delete Cluster
==============

.. http:delete:: /clusters/(uuid:id)

  Delete a cluster.

  **Example request**:

  .. code-block:: http

    DELETE /clusters HTTP/1.1
    Accept: application/json

  **Example response**:

  .. code-block:: http

    HTTP/1.1 202 Accepted

  :statuscode 400: Bad Request
  :statuscode 204: Successfully Deleted
