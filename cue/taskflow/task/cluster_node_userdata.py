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

import email.mime.multipart as mime_multipart
import email.mime.text as mime_text
import sys

import pystache
import taskflow.task as task


_userdata_cloud_config = """hostname: {{node_name}}
manage_etc_hosts: false
"""

_userdata_script_1 = """#!/bin/bash
cat > /etc/hosts << EOF
127.0.0.1 localhost
"""

_userdata_script_2 = """
EOF

if [[ ! "`grep rabbitmq /etc/passwd`" ]]; then
  useradd -d /var/lib/rabbitmq -U -m rabbitmq
fi

mkdir -p /etc/rabbitmq /var/lib/rabbitmq
echo {{erlang_cookie}} > /var/lib/rabbitmq/.erlang.cookie
chmod 0400 /var/lib/rabbitmq/.erlang.cookie

cat > /etc/rabbitmq/rabbitmq.config << EOF
[
  {rabbit, [
        {cluster_nodes, {["""

_userdata_script_3 = """], disc}}
  ]}
].
EOF

chown -R rabbitmq:rabbitmq /var/lib/rabbitmq
apt-get update
apt-get install -y rabbitmq-server
"""


class ClusterNodeUserData(task.Task):
    default_provides = 'userdata'

    def __init__(self, name, node_count, node_ip_prefix, inject=None):
        requires = ["%s%d" % (node_ip_prefix, i) for i in range(node_count)]
        requires.append('erlang_cookie')
        requires.append('node_name')

        super(ClusterNodeUserData, self).__init__(name=name,
                                                  requires=requires,
                                                  inject=inject)

        self.userdata_script = _userdata_script_1
        for i in range(node_count):
            host = "{{%s%d}} rabbit-node-%d\n" % (node_ip_prefix, i, i)
            self.userdata_script += host

        self.userdata_script += _userdata_script_2
        for i in range(node_count):
            self.userdata_script += "'rabbit@rabbit-node-%d'," % i
        self.userdata_script = self.userdata_script[:-1]

        self.userdata_script += _userdata_script_3

    def execute(self, *args, **kwargs):
        userdata = mime_multipart.MIMEMultipart()

        cloud_config = pystache.render(_userdata_cloud_config, kwargs)
        sub_message = mime_text.MIMEText(cloud_config,
                               'cloud-config',
                               sys.getdefaultencoding())
        sub_message.add_header('Content-Disposition',
                               'attachment; filename="cloud_config"')
        userdata.attach(sub_message)

        script = pystache.render(self.userdata_script, kwargs)
        sub_message = mime_text.MIMEText(script,
                               'x-shellscript',
                               sys.getdefaultencoding())
        sub_message.add_header('Content-Disposition',
                               'attachment; filename="setup_rabbitmq.sh"')
        userdata.attach(sub_message)
        return userdata.as_string()