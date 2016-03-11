************************
Installing Cue on Ubuntu
************************

This install guide provides details on how to install on a Ubuntu based image
with the necessary dependencies and required configuration.

.. include:: overview.rst


.. _install-ubuntu-prerequisites:

Prerequisites
=============

.. _install-ubuntu-prereq-install:

Install
^^^^^^^
::

    $ sudo apt-get install zookeeper zookeeperd python-mysqldb

.. _install-ubuntu-prereq-setup-mysql:

MySQL
^^^^^

.. note::

    The following commands should be done using the mysql command line or similar.

Create the MySQL user

::

    $ GRANT ALL ON cue.* TO 'cue'@'localhost' IDENTIFIED BY 'cue'

Create the database

::

    $ CREATE DATABASE cue

.. _install-ubuntu-source:

Installing using Source (Git)
=============================

1. Install pre-requisites:

::

    $ sudo apt-get install git python-dev python-pip
    $ sudo apt-get build-dep python-lxml

2. Clone the repository:

::

    $ git clone git://github.com/openstack/cue cue

3. Change directory to the newly cloned repository

::

     $ cd cue

4. Install all dependencies using pip

::

    $ sudo pip install -r requirements.txt
    $ sudo pip install MySQL-python

5. Install Cue:

::

    $ sudo python setup.py develop

6. Copy over configuration files

::

    $ sudo cp -R etc/cue /etc/
    $ ls /etc/cue/*.sample | while read f; do sudo cp $f $(echo $f | sed "s/.sample$//g"); done

Create directories
^^^^^^^^^^^^^^^^^^

Since we are not running packages some directories are not created for us.

::

    $ sudo mkdir /var/lib/cue /var/log/cue
    # Needed if you are running cue as a non root user.
    $ sudo chown cue_user /var/lib/cue /var/log/cue


Configuring
===========

Register Cue with Keystone
^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Create new user for cue service
::

    keystone user-create --name cue --tenant <tenant_uuid> --pass <password

2. Add admin role for cue_admin user
::

    keystone user-role-add --user cue_admin --tenant cue_admin_service --role=admin


Add Cue Service Endpoint to Keystone
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Add cue service to keystone
::

    keystone service-create --type message-broker --name cue --description "Message Broker provisioning service"

2. Create a new endpoint for the cue service in keystone
::

    keystone endpoint-create --region RegionOne --service <cue_service_uuid> --publicurl http://<cue_api_ip>:8795/ --adminurl http://<cue_api_ip>:8795/ --internalurl http://<cue_api_ip>:8795/


Create Message Broker Image
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Cue service makes use of custom Ubuntu images with required messaging broker (e.g. RabbitMQ)
installed.  Building images uses the Tripleo  `diskimage-builder` tools.  Image elements for
the RabbitMQ image are found in cue/contrib/image-elements/, you will also find the
'image-build-rabbitmq.sh' script which will build a custom image compatible with Cue.

The images are based on the latest base Ubuntu cloud image with the following elements:

* os-apply-config
* os-refresh-config
* ntp
* hosts
* cue-rabbitmq-base (cue/contrib/image-elements/cue-rabbit-base)
* ifmetric (cue/contrib/image-elements/ifmetric)

Note: building images will require a machine with more than 4GB of memory.

Once the image is built, it must be uploaded to Glance (disk format is qcow2) and message broker
details added to Cue database through cue-management.

1. Create new Message Broker and set it as active broker
::

   $ cue-manage --config-file etc/cue/cue.conf broker add <name> true

2. Add metadata indicating image id (created above) for new Message Broker
::

   $ cue-manage --config-file etc/cue/cue.conf broker add_metadata <broker-uuid> --image <image-uuid>

Cue Config
^^^^^^^^^^

::

  $ sudo editor /etc/cue/cue.conf

Copy or mirror the configuration from this sample file here:

.. literalinclude:: ../examples/example-cue.conf
   :language: ini

More details on configuration values:

.. toctree::
   :glob:
   :maxdepth: 1

   ../configuration

Sync Database schemas
^^^^^^^^^^^^^^^^^^^^^

Initialize database schema for Cue
::

    $ cue-manage --config-file /etc/cue/cue.conf database upgrade

Notes:

* magement_network_id must be different than provided user network id through API.

Starting the services
=====================

Worker
^^^^^^
::

    $ cue-worker --config-file /etc/cue/cue.conf

API
^^^

The API can be started as is (through shell) or can be started behind Apache.
Starting the API behind Apache is the recommended method for running the API
(section below).

Starting with command shell::

    $ cue-api --config-file /etc/cue/cue.conf


.. include:: ../howtos/apache.rst
