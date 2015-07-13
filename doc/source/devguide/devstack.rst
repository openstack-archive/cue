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

.. _devstack:

========
DevStack
========

Instructions on how to install Cue as part of a DevStack deployment.

Instructions
++++++++++++

1. Get a clean Ubuntu 14.04 VM. DevStack "takes over". Don't use your desktop!
    Note: Ensure VM has at least 8GB of Memory.

2. Clone Cue and DevStack inside the VM::

   $ git clone https://git.openstack.org/openstack-dev/devstack
   $ git clone https://github.com/openstack/cue.git

3. Install the Cue extension for DevStack::

   $ cd cue/contrib/devstack
   $ ./install.sh

4. Copy local.conf and local.sh from cue/contrib/devstack::

   $ cp local.* ../../../devstack/

5. Run DevStack::

   $ cd ../../../devstack
   $ ./stack.sh

6. Enter the screen sessions "shell" window::

   $ ./rejoin-stack.sh

   Then press Ctrl+A followed by d to exit

7. Load desired credentials into the shell::

   $ source openrc admin admin # For the admin user, admin tenant
   $ source openrc admin demo  # For the admin user, demo tenant
   $ source openrc demo demo   # For the demo user, demo tenant

8. Try out the cue client::

       $ openstack message-broker cluster create --name cluster_01 --nic d5c35f43-4e8e-4264-9c8a-21c2f0a358e8 --flavor 8795 --size 1
       +------------+-------------------------------------------+
       | Field      | Value                                     |
       +------------+-------------------------------------------+
       | created_at | 2015-06-02T21:29:15+00:00                 |
       | end_points | []                                        |
       | flavor     | 8795                                      |
       | id         | b7ed9907-2d37-41e6-b70c-22eb1ea44777      |
       | name       | cluster_01                                |
       | network_id | [u'd5c35f43-4e8e-4264-9c8a-21c2f0a358e8'] |
       | size       | 1                                         |
       | status     | BUILDING                                  |
       +------------+-------------------------------------------+

       $ openstack message-broker cluster list
       +--------------------------------------+------------+----------+------------+
       | id                                   | name       | status   | end_points |
       +--------------------------------------+------------+----------+------------+
       | b7ed9907-2d37-41e6-b70c-22eb1ea44777 | cluster_01 | BUILDING | []         |
       +--------------------------------------+------------+----------+------------+

       $ openstack message-broker cluster show b7ed9907-2d37-41e6-b70c-22eb1ea44777
       +------------+------------------------------------------------+
       | Field      | Value                                          |
       +------------+------------------------------------------------+
       | created_at | 2015-06-02T21:29:15+00:00                      |
       | end_points | [{u'type': u'AMQP', u'uri': u'10.0.0.5:5672'}] |
       | flavor     | 8795                                           |
       | id         | b7ed9907-2d37-41e6-b70c-22eb1ea44777           |
       | name       | cluster_01                                     |
       | network_id | [u'd5c35f43-4e8e-4264-9c8a-21c2f0a358e8']      |
       | size       | 1                                              |
       | status     | ACTIVE                                         |
       | updated_at | 2015-06-02T21:29:18+00:00                      |
       +------------+------------------------------------------------+

