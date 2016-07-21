# Copyright (c) 2011 OpenStack Foundation
# All Rights Reserved.
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

"""Policy Engine For Cue."""

from oslo_config import cfg
from oslo_log import log as logging
from oslo_policy import opts
from oslo_policy import policy

from cue.common import exception
from cue.common.i18n import _  # noqa
from cue.common.i18n import _LI  # noqa
from cue.common import utils


LOG = logging.getLogger(__name__)

CONF = cfg.CONF

# Add the default policy opts
opts.set_defaults(CONF)

_ENFORCER = None


def reset():
    global _ENFORCER
    if _ENFORCER:
        _ENFORCER.clear()
    _ENFORCER = None


def init(default_rule=None):
    policy_files = utils.find_config(CONF['oslo_policy'].policy_file)

    if len(policy_files) == 0:
        msg = 'Unable to determine appropriate policy json file'
        raise exception.ConfigurationError(msg)

    LOG.info(_LI('Using policy_file found at: %s') % policy_files[0])

    with open(policy_files[0]) as fh:
        policy_string = fh.read()
    rules = policy.Rules.load_json(policy_string, default_rule=default_rule)

    global _ENFORCER
    if not _ENFORCER:
        LOG.debug("Enforcer is not present, recreating.")
        _ENFORCER = policy.Enforcer(cfg.CONF)

    _ENFORCER.set_rules(rules)


def check(rule, ctxt, target=None, do_raise=True, exc=exception.NotAuthorized):
    # creds = ctxt.to_dict()
    creds = ctxt.to_policy_values()

    # import ipdb; ipdb.set_trace()
    target = target or {}

    try:
        result = _ENFORCER.enforce(rule, target, creds, do_raise, exc)
    except Exception:
        result = False
        raise
    else:
        return result
    finally:
        extra = {'policy': {'rule': rule, 'target': target}}

        if result:
            LOG.info(_("Policy check succeeded for rule '%(rule)s' "
                       "on target %(target)s") %
                     {'rule': rule, 'target': repr(target)}, extra=extra)
        else:
            LOG.info(_("Policy check failed for rule '%(rule)s' "
                       "on target %(target)s") %
                     {'rule': rule, 'target': repr(target)}, extra=extra)
