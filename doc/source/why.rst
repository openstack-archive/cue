========
Why Cue?
========

Messaging is a common development pattern for building loosely coupled
distributed systems. Messaging systems act as glue between independent
applications. Dozens of off-the-shelf products exist that implement messaging
and queuing semantics, many of which implement open protocols such as AMQP 0.9
and 1.0.

There is a significant operational burden associated with the lifecycle
management of message brokers in an enterprise. Not to mention the time
associated with ensuring the broker is deployed in a cloud native pattern,
assuming failure of underlying infrastructure.  Cue aims to simplify the
provisioning and management of messaging systems, providing high availability
and auto-healing capabilities for both the cloud operator and end user, while
providing secure tenant-level isolation.

The main goal of this service is to simplify the end user application
development lifecycle for both legacy and "cloud native" applications, allowing
the developer to focus on their application, instead of the underlying
middleware services.