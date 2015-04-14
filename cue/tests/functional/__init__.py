# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Authors: Davide Agnello <davide.agnello@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Copyright [2014] Hewlett-Packard Development Company, L.P.
# limitations under the License.

import zake.fake_client as fake_client

import cue.taskflow.client as tf_client

_zk_client = fake_client.FakeClient()
persistence = tf_client.create_persistence(client=_zk_client)
jobboard = tf_client.create_jobboard("test_board",
                                     persistence=persistence,
                                     client=_zk_client)

tf_client = tf_client.get_client_instance(persistence=persistence,
                                          jobboard=jobboard)
