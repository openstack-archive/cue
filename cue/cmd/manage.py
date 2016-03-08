# -*- encoding: utf-8 -*-
# Copyright 2015 Hewlett-Packard Development Company, L.P.
# Copyright 2012 Bouvet ASA
#
# Author: Endre Karlson <endre.karlson@bouvet.no>
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
import sys

from oslo_config import cfg
from oslo_log import log
from stevedore import extension

from cue.common import config
from cue import version


CONF = cfg.CONF


def methods_of(obj):
    """Utility function to get all methods of a object

    Get all callable methods of an object that don't start with underscore
    returns a list of tuples of the form (method_name, method).
    """
    result = []
    for i in dir(obj):
        if callable(getattr(obj, i)) and not i.startswith('_'):
            result.append((i, getattr(obj, i)))
    return result


def get_available_commands():
    em = extension.ExtensionManager('cue.manage')
    return dict([(e.name, e.plugin) for e in em.extensions])


def add_command_parsers(subparsers):
    for category, cls in get_available_commands().items():
        command_object = cls()

        parser = subparsers.add_parser(category)
        parser.set_defaults(command_object=command_object)

        category_subparsers = parser.add_subparsers(dest='action')

        for (action, action_fn) in methods_of(command_object):
            action = getattr(action_fn, '_cmd_name', action)
            parser = category_subparsers.add_parser(action)

            action_kwargs = []
            for args, kwargs in getattr(action_fn, 'args', []):
                parser.add_argument(*args, **kwargs)

            parser.set_defaults(action_fn=action_fn)
            parser.set_defaults(action_kwargs=action_kwargs)


category_opt = cfg.SubCommandOpt('category', title="Commands",
                                 help="Available Commands",
                                 handler=add_command_parsers)


def get_arg_string(args):
    arg = None
    if args[0] == '-':
        # (Note)zhiteng: args starts with FLAGS.oparser.prefix_chars
        # is optional args. Notice that cfg module takes care of
        # actual ArgParser so prefix_chars is always '-'.
        if args[1] == '-':
            # This is long optional arg
            arg = args[2:]
        else:
            arg = args[1:]
    else:
        arg = args

    return arg


def fetch_func_args(func):
    fn_args = []
    for args, kwargs in getattr(func, 'args', []):
        arg = kwargs.get('dest', get_arg_string(args[0]))
        fn_args.append(getattr(CONF.category, arg))

    return fn_args


def main(argv=None, conf_fixture=None):
    if argv is None:    # pragma: no cover
        argv = sys.argv

    # Registering cli options directly to the global cfg.CONF causes issues
    # for unit/functional tests that test anything but the cmd.manage module
    # because cmd.manage adds required cli parameters.  A conf_fixture object
    # is expected to be passed in only during tests.
    if conf_fixture is None:    # pragma: no cover
        CONF.register_cli_opt(category_opt)
    else:
        conf_fixture.register_cli_opt(category_opt)

    log.register_options(CONF)
    config.set_defaults()

    CONF(argv[1:], project='cue',
         version=version.version_info.version_string())

    log.setup(CONF, "cue")

    fn = CONF.category.action_fn

    fn_args = fetch_func_args(fn)
    fn(*fn_args)
