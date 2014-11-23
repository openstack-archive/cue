..
    Copyright 2014 Hewlett-Packard Development Company, L.P.

    Licensed under the Apache License, Version 2.0 (the "License"); you may
    not use this file except in compliance with the License. You may obtain
    a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.

.. _getting-started:

===============
Getting Started
===============

Cue is comprised of three cue components :ref:`cue-api`, supported by a few standard open source components.

There are many different options for customizing Designate, and two of these options
have a major impact on the installation process:

* The storage backend used (SQLite or MySQL)

This guide will walk you through setting up a typical development environment for Cue.

For this guide you will need access to an Ubuntu Server (14.04).  Other platforms:

- `Fedora 19 Notes`_

.. _Development Environment:

Development Environment
+++++++++++++++++++++++

Installing Cue
==============

.. index::
   double: install; cue

1. Install system package dependencies (Ubuntu)

::

   $ apt-get install python-pip python-virtualenv
   $ apt-get build-dep python-lxml

2. Clone the Cue repo from GitHub

::

   $ git clone https://github.com/stackforge/cue.git
   $ cd cue


3. Setup virtualenv

.. note::
   This is an optional step, but will allow Cue's dependencies
   to be installed in a contained environment that can be easily deleted
   if you choose to start over or uninstall Cue.

::

   $ virtualenv --no-site-packages .venv
   $ . .venv/bin/activate


4. Install Cue and its dependencies

::

   $ pip install -r requirements.txt -r test-requirements.txt
   $ python setup.py develop


5. Change directories to the etc/cue folder.

.. note::
    Everything from here on out should take place in or below your cue/etc folder

::

   $ cd etc/cue


6. Create Cue's config files by copying the sample config files

::

   $ ls *.sample | while read f; do cp $f $(echo $f | sed "s/.sample$//g"); done


7. Make the directory for Cue log files

::

   $ mkdir /var/log/cue


Configuring Cue
===============

.. index::
    double: configure; cue

Open the cue.conf file for editing

::

  $ editor cue.conf


Copy or mirror the configuration from this sample file here:

.. literalinclude:: examples/example-cue.conf
    :language: ini

Installing MySQL
================

.. index::
    double: install; mysql

Install the MySQL server package

::

    $ apt-get install mariadb-server


If you do not have MySQL previously installed, you will be prompted to change the root password.
By default, the MySQL root password for Designate is "password". You can:

* Change the root password to "password"
* If you want your own password, edit the cue.conf file and change any instance of
   "mysql://root:password@127.0.0.1/cue" to "mysql://root:YOUR_PASSWORD@127.0.0.1/cue"

You can change your MySQL password anytime with the following command::

    $ mysqladmin -u root -p password NEW_PASSWORD
    Enter password <enter your old password>

Create the Designate and PowerDNS tables

::

    $ mysql -u root -p
    Enter password: <enter your password here>

    mysql> CREATE DATABASE `cue` CHARACTER SET utf8 COLLATE utf8_general_ci;
    mysql> exit;


Install additional packages

::

    $ apt-get install libmysqlclient-dev
    $ pip install mysql-python


If you intend to run Cue as a non-root user, then sudo permissions need to be granted

::

   $ echo "cue ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers.d/90-cue
   $ sudo chmod 0440 /etc/sudoers.d/90-cue


Initialize & Start the API Service
==================================

.. index::
   double: install; api

::

   #Sync the Cue database:
   $ cue-manage --config-file etc/cue/cue.conf database upgrade

   #Start the api service:
   $ cue-api --config-file etc/cue/cue.conf

You'll now be seeing the log from the api service.


Exercising the API
==================

.. note:: If you have a firewall enabled, make sure to open port 53, as well as Cue's default port (6385).

Using a web browser, curl statement, or a REST client, calls can be made to the Cue API using the following format where “command” is any of the commands listed in the :doc:`rest`

You can find the IP Address of your server by running

::

   wget http://ipecho.net/plain -O - -q ; echo


Fedora 19 Notes
===============

Most of the above instructions under `Installing Designate`_ should work.  There are a few differences when working with Fedora 19:

Installing Designate on Fedora
------------------------------

Installing the basic Fedora packages needed to install Designate:

::

   $ yum install gcc git yum-utils
   $ yum install python-pip python-virtualenv python-pbr
   $ yum-builddep python-lxml

Use **/var/lib/cue** as the root path for databases and other variable state files, not /root/cue

::

   $ mkdir -p /var/lib/cue

Installing MySQL
----------------

The MySQL Fedora packages are **mysql mysql-server mysql-devel**

::

    $ yum install mysql mysql-server mysql-devel
    $ pip install mysql-python

You will have to change the MySQL password manually.

::

    $ systemctl start mysqld.service
    $ mysqladmin -u root password NEW_PASSWORD
        # default password for Cue is 'password'

::
