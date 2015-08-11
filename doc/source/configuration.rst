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

..  |br| raw:: html

   <br />

.. _configuration:

=======================
 Configuration Options
=======================

[DEFAULT]
=========

===============================  ====================================  ===================================================
Parameter                        Default                               Note
===============================  ====================================  ===================================================
management_network_id            None                                  The id representing the management network
os_security_group                None                                  The default Security to access clustered VMs
default_broker_name              rabbitmq                              The name of the default broker image
rabbit_port                      5672                                  RabbitMQ AMQP port on clustered VMs
policy_file                      /etc/cue/policy.json                  JSON file representing policy
verbose                          false                                 Print more verbose output
debug                            false                                 Print debugging output
state-path                       /var/lib/cue                          Top-level directory for maintaining cue's state
===============================  ====================================  ===================================================

[database]
==========

==========================  ====================================  ==============================================================
Parameter                   Default                               Note
==========================  ====================================  ==============================================================
connection                  None                                  The SQLAlchemy connection string to database
==========================  ====================================  ==============================================================

[api]
=====

===========================  ====================================  ==============================================================
Parameter                    Default                               Note
===========================  ====================================  ==============================================================
host_ip                      0.0.0.0                               The listen IP for the Cue API server
port                         8795                                  The port for the Cue API server
max_limit                    1000                                  The maximum number of items returned in a single response
max_cluster_size             10                                    Maximum number of nodes in a cluster
auth_strategy                keystone                              Method to use for authentication: noauth or keystone
pecan_debug                  False                                 Pecan HTML Debug Interface
===========================  ====================================  ==============================================================

[taskflow]
==========

=============================  ====================================  ==============================================================
Parameter                      Default                               Note
=============================  ====================================  ==============================================================
persistence_connection         None                                  Persistence connection
zk_hosts                       localhost                             Zookeeper jobboard hosts
zk_path                        /cue/taskflow                         Zookeeper path for jobs
zk_timeout                     10                                    Zookeeper operations timeout
jobboard_name                  'cue'                                 Board name
engine_type                    'serial'                              Engine type
cluster_node_check_timeout     10                                    Number of seconds between node status checks
cluster_node_check_max_count   30                                    Number of times to check a node for status
=============================  ====================================  ==============================================================

[openstack]
===========

===========================  ====================================  ==============================================================
Parameter                    Default                               Note
===========================  ====================================  ==============================================================
os_region_name               None                                  Region name
os_tenant_id                 None                                  Openstack Tenant ID
os_tenant_name               None                                  Openstack Tenant Name
os_username                  None                                  Openstack Username
os_password                  None                                  Openstack Password
os_auth_url                  None                                  Openstack Authentication (Identity) URL
os_auth_version              None                                  Openstack Authentication (Identity) Version
os_project_name              None                                  Openstack Project Name
os_project_domain_name       None                                  Openstack Project Domain Name
os_user_domain_name          None                                  Openstack User Domain Name
os_key_name                  None                                  SSH key to be provisioned to cue VMs
os_availability_zone         None                                  Default availability zone to provision cue VMs
===========================  ====================================  ==============================================================

[keystone_authtoken]
====================

===========================  ====================================  ==============================================================
Parameter                    Default                               Note
===========================  ====================================  ==============================================================
auth_url                     None                                  The URL to Keystone Identity Service
auth_plugin                  None                                  Name of the plugin to load
project_name                 None                                  Project name accessing Keystone (usually 'service')
username                     None                                  Username for accessing Keystone
password                     None                                  password for accessing keystone
===========================  ====================================  ==============================================================