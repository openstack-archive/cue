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
import time
import urllib
import urllib2

import taskflow.task


class GetRabbitClusterStatus(taskflow.task.Task):
    def __init__(self,
                 retry_delay_seconds=None,
                 retry_delay_ms=None,
                 name=None,
                 **kwargs):
        """Constructor

        This constructor sets the retry delay for this task's revert method.

        :param retry_delay_seconds: retry delay in seconds
        :param retry_delay_ms: retry delay in milliseconds
        :param name: unique name for atom
        """
        super(GetRabbitClusterStatus, self).__init__(name=name, **kwargs)

        self.sleep_time = 0
        if retry_delay_seconds:
            self.sleep_time = retry_delay_seconds

        if retry_delay_ms:
            self.sleep_time += retry_delay_ms / 1000.0

    def execute(self,
                vm_ip,
                default_rabbit_user,
                default_rabbit_pass,
                **kwargs):
        """Main execute method to verify Rabbitmq clustering in a VM

        :param vm_ip: VM ip address
        :type vm_ip: string
        """
        vhosts_url = 'http://' + vm_ip + ':15672/api/vhosts'
        aliveness_url = 'http://' + vm_ip + ':15672/api/aliveness-test/'

        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None,
                                  vhosts_url,
                                  default_rabbit_user,
                                  default_rabbit_pass)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        try:
            res = opener.open(vhosts_url)
        except (urllib2.HTTPError, urllib2.URLError) as err:
            print "Failed to open url:  " + vhosts_url + "\n" + str(err)
        json_res = json.load(res)

        rabbit_up = False
        while not rabbit_up:
            result = {}
            for x in json_res:
                vhost = urllib.quote(x['name'], '')
                cur_aliveness_url = aliveness_url + vhost

                password_mgr.add_password(None,
                                          cur_aliveness_url,
                                          default_rabbit_user,
                                          default_rabbit_pass)
                handler = urllib2.HTTPBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(handler)
                res = opener.open(cur_aliveness_url)

                result[x['name']] = json.load(res)['status']
            if all(val == 'ok' for val in result.values()):
                rabbit_up = True
            else:
                time.sleep(0.5)

    def revert(self, *args, **kwargs):
        """Revert GetRabbitClusterStatus

        This method is executed upon failure of the GetRabbitClusterStatus or
        the Flow that the Task is part of.

        :param args: positional arguments that the task required to execute.
        :type args: list
        :param kwargs: keyword arguments that the task required to execute; the
                       special key `result` will contain the :meth:`execute`
                       results (if any) and the special key `flow_failures`
                       will contain any failure information.
        """
        if self.sleep_time != 0:
            time.sleep(self.sleep_time)