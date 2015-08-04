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

************************************
Development Environment with Vagrant
************************************

Cue is comprised of three main components :ref:`cue-api`, :ref:`cue-worker` and :ref:`cue-manage`.
The Cue project includes a Vagrant configuration which deploys the Cue service and related
scenario tests as part of a DevStack installation.  This configuration allows new developers to
get up and running quickly and efficiently.


This guide will walk you through setting up a Vagrant VM with devstack and Cue installed.


.. _Development Environment:

Development Environment
+++++++++++++++++++++++
The Vagrant configuration allows the deployment of Cue service into DevStack.
This environment provides a developer with a quick and easy way to run Cue with latest
changes locally, run integration and scenario tests.

Deploying Cue Through Vagrant
=============================

.. index::
   double: deploy; cue

1. Clone the Cue repo from GitHub

::

   $ git clone https://github.com/openstack/cue.git


2. Startup Vagrant VM

::

    $ cd cue/contrib/vagrant
    $ vagrant up ubuntu

3. SSH into Vagrant VM

::

    $ vagrant ssh ubuntu

4. Install Devstack

::

    $ cd devstack
    $ ./stack.sh


You are now in the Vagrant VM with DevStack installed/configured with Cue API,
and Cue Worker.

Unit and Functional Testing
===========================

Unit are located in:
cue/cue/tests/unit

Functional tests are located in:
cue/cue/tests/functional

To run all unit and function tests, execute 'tox' from Cue project folder:
::

   $ cd cue
   $ tox


Integration Tests
=================

Integration tests verify Cue through calling the REST API directly.  These tests make use of the Tempest framework and are located in:
cue/tests/integration

To run all integration tests, ssh into the Vagrant VM with DevStack/Cue installation (above) and run the following script:
::

   $ ./cue/tests/integration/run_tests.sh


Scenario Tests
==============

Scenario tests verify Cue through the Python Cue Client.  These tests make use of Rally Benchmark framework and are located in:
cue/rally-jobs

To run all scenario tests, ssh into the Vagrant VM with DevStack/Cue installation (above) and run the following script:
::

   $ rally task start --task ~/cue/rally-jobs/rabbitmq-scenarios.yaml
