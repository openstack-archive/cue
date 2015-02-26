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

Running Cue API behind Apache2
==============================

.. note::
    In this howto we explain how to setup cue-api to run behind a Apache2
    instance vs as a process of it's own.

    We will assume that cue is available under /opt/stack/cue as it is in
    devstack.


Symlink app.wsgi to /var/www

::

    $ sudo mkdir /var/www/cue
    $ sudo ln -s /opt/stack/cue/cue/api/app.wsgi /var/www/cue

Setup Apache2 config

::

    $ sudo cp /opt/cue/etc/apache2/cue.conf /etc/apache2/sites-available
    $ sudo a2ensite cue
    $ sudo service apache2 reload

You should now have cue-api running under Apache2!
