# Copyright 2016 Hewlett Packard Enterprise Development Corporation, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from oslo_config import cfg
from oslo_middleware import cors


def set_defaults():
    """Set all oslo.config default overrides for cue."""
    set_cors_middleware_defaults()


def set_cors_middleware_defaults():
    """Update default configuration options for oslo.middleware."""
    # CORS Defaults
    # TODO(krotscheck): Update with https://review.openstack.org/#/c/285368/
    cfg.set_defaults(cors.CORS_OPTS,
                     allow_headers=['X-Auth-Token',
                                    'X-Server-Management-Url'],
                     expose_headers=['X-Auth-Token',
                                     'X-Server-Management-Url'],
                     allow_methods=['GET',
                                    'PUT',
                                    'POST',
                                    'DELETE',
                                    'PATCH']
                     )
