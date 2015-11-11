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

import json
import urllib
import urllib2

import taskflow.task


class GetRabbitClusterStatus(taskflow.task.Task):
    def execute(self,
                vm_ip,
                default_rabbit_user,
                default_rabbit_pass,
                proto=None,
                **kwargs):
        """Main execute method to verify Rabbitmq clustering in a VM

        :param vm_ip: VM ip address
        :type vm_ip: string
        :param default_rabbit_user: Username for RabbitMQ
        :type default_rabbit_user: string
        :param default_rabbit_pass: Password for RabbitMQ
        :type default_rabbit_pass: string
        :param proto: Protocol for url, http/https
        :type proto: string
        """
        if not proto:
            proto = 'http'

        base_url = proto + '://' + vm_ip + ':15672/api'

        # RMQ management url to get a list of the existing vhosts
        vhosts_url = base_url + '/vhosts'
        # RMQ management url to query whether the RMQ nodes have clustered
        aliveness_url = base_url + '/aliveness-test'

        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None,
                                  vhosts_url,
                                  default_rabbit_user,
                                  default_rabbit_pass)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)

        retval = "NOT-OK"

        try:
            res = opener.open(vhosts_url)
        except urllib2.URLError:
            pass
        else:
            json_res = json.load(res)

            result = {}
            for x in json_res:
                vhost = urllib.quote(x['name'], '')
                cur_aliveness_url = aliveness_url + '/' + vhost

                password_mgr.add_password(None,
                                          cur_aliveness_url,
                                          default_rabbit_user,
                                          default_rabbit_pass)
                handler = urllib2.HTTPBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(handler)
                res = opener.open(cur_aliveness_url)

                result[x['name']] = json.load(res)['status']
            if all(val == 'ok' for val in result.values()):
                retval = 'OK'

        return retval
