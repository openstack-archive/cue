============
What is Cue?
============

Cue is a message broker provisioning service for Openstack. Its goal is to
simplify and automate the complex tasks of provisioning, management, and
administration of message brokers. Cue is designed to provide API, CLI, and UI
based management of open source brokers such as RabbitMQ and Kafka. Because
it’s designed to be pluggable, proprietary message brokers can also be
delivered as a service through Cue.  The service will provide resource
isolation at the VM level, and does not attempt to implement multi-tenancy at
the message broker layer.

There are two personas to keep in mind when thinking about Cue. One is the
Cloud Operator. The Cloud Operator installs and operates Cue, alongside the
rest of OpenStack. This person cares about Cue installation and upgrades, along
with broker level availability and versioning capabilities. The second persona
is the application developer. This person provisions message broker clusters
from the Cue API, CLI, or Horizon console. Alternatively, the application
developer consumes Cue through a Platform as a Service product such as Cloud
Foundry. In this scenario there is already a Cue provisioned cluster and the
developer simply specifies that a queue of a certain name is needed in the
application’s manifest file. At deploy time, the queue is created directly on
the message broker itself using a Cloud Foundry service broker.