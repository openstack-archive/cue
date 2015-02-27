# -*- coding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pystache

import taskflow.task as task


_userdata_template_1 = """
#!/bin/bash

cat > /etc/hosts << EOF
127.0.0.1 localhost
"""

_userdata_template_2 = """
EOF

apt-get install -y rabbitmq-server
rabbitmqctl stop_app
rabbitmqctl reset
rabbitmqctl stop

echo {{erlang_cookie}} > /var/lib/rabbitmq/.erlang.cookie

cat > /etc/rabbitmq/rabbitmq.conf << EOF
[
  {rabbit, [
        {cluster_nodes, {["""

_userdata_template_3 = """], disc}}
  ]}
].
EOF

rabbitmq-server -detached
"""


class ClusterNodeUserData(task.Task):
    default_provides = 'userdata'

    def __init__(self, name, node_count, node_ip_prefix):
        requires = ["%s%d" % (node_ip_prefix, i) for i in range(node_count)]
        super(ClusterNodeUserData, self).__init__(name=name, requires=requires)

        self.userdata_template = _userdata_template_1
        for i in range(node_count):
            host = "{{%s%d}} rabbit-node-%d\n" % (node_ip_prefix, i, i)
            self.userdata_template += host

        self.userdata_template += _userdata_template_2
        for i in range(node_count):
            self.userdata_template += "'rabbit@rabbit-node-%d',"
        self.userdata_template = self.userdata_template[:-1]

    def execute(self, *args, **kwargs):
        userdata = pystache.render(self.userdata_template, kwargs)
        return userdata