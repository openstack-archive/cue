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

from oslo.config import cfg

from cue.common import exception
from cue.common.i18n import _  # noqa
from cue.common.i18n import _LI  # noqa
from cue.openstack.common import log as logging
from cue.openstack.common import policy


LOG = logging.getLogger(__name__)


_ENFORCER = None


def reset():
    global _ENFORCER
    if _ENFORCER:
        _ENFORCER.clear()
    _ENFORCER = None


def set_rules(data, default_rule=None, overwrite=True):
    default_rule = default_rule or cfg.CONF.policy_default_rule
    if not _ENFORCER:
        LOG.debug("Enforcer not present, recreating at rules stage.")
        init()

    if default_rule:
        _ENFORCER.default_rule = default_rule

    msg = "Loading rules %s, default: %s, overwrite: %s"
    LOG.debug(msg, data, default_rule, overwrite)

    if isinstance(data, dict):
        rules = dict((k, policy.parse_rule(v)) for k, v in data.items())
        rules = policy.Rules(rules, default_rule)
    else:
        rules = policy.Rules.load_json(data, default_rule)

    _ENFORCER.set_rules(rules, overwrite=overwrite)


def init(default_rule=None):
    if "config_dir" in cfg.CONF:
        policy_file = cfg.CONF.find_file(cfg.CONF.policy_file)
    else:
        policy_file = cfg.CONF.pybasedir + '/etc/cue/' + cfg.CONF.policy_file

    if len(policy_file) == 0:
        msg = 'Unable to determine appropriate policy json file'
        raise exception.ConfigurationError(msg)

    LOG.info(_LI('Using policy_file found at: %s') % policy_file)

    with open(policy_file) as fh:
        policy_string = fh.read()
    rules = policy.Rules.load_json(policy_string, default_rule=default_rule)

    global _ENFORCER
    if not _ENFORCER:
        LOG.debug("Enforcer is not present, recreating.")
        _ENFORCER = policy.Enforcer()

    _ENFORCER.set_rules(rules)


def check(rule, ctxt, target=None, do_raise=True, exc=exception.NotAuthorized):
    creds = ctxt.to_dict()
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
