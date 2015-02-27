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

import jinja2
import taskflow.task as task


class ClusterNodeUserData(task.Task):
    default_provides = 'userdata'

    def __init__(self, name, node_count, node_ip_prefix, inject=None):
        requires = ["%s%d" % (node_ip_prefix, i) for i in range(node_count)]
        requires.append('erlang_cookie')
        requires.append('node_name')

        super(ClusterNodeUserData, self).__init__(name=name,
                                                  requires=requires,
                                                  inject=inject)

        self.node_count = node_count
        self.node_ip_prefix = node_ip_prefix
        env = jinja2.Environment(
            loader=jinja2.PackageLoader('cue', 'templates'))
        self.cloud_config_template = env.get_template('cloud_config.tmpl')
        self.userdata_template = env.get_template('install_rabbit.sh.tmpl')

    def execute(self, *args, **kwargs):
        userdata = mime_multipart.MIMEMultipart()

        rabbit_nodes = {"rabbit-node-%d" % i:
                            kwargs["%s%d" % (self.node_ip_prefix, i)]
                        for i in range(self.node_count)}

        cloud_config = self.cloud_config_template.render(
            node_name=kwargs['node_name'])

        sub_message = mime_text.MIMEText(cloud_config,
                               'cloud-config',
                               sys.getdefaultencoding())
        sub_message.add_header('Content-Disposition',
                               'attachment; filename="cloud_config"')
        userdata.attach(sub_message)

        userdata_inputs = {
            'rabbit_nodes': rabbit_nodes,
            'erlang_cookie': kwargs['erlang_cookie'],
        }
        script = self.userdata_template.render(userdata_inputs)
        sub_message = mime_text.MIMEText(script,
                               'x-shellscript',
                               sys.getdefaultencoding())
        sub_message.add_header('Content-Disposition',
                               'attachment; filename="setup_rabbitmq.sh"')
        userdata.attach(sub_message)
        return userdata.as_string()