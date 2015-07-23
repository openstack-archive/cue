# Copyright 2014 Hewlett-Packard Development Company, L.P.
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

from cue.common.i18n import _LE  # noqa
from cue.objects import utils as obj_utils

import collections

from oslo_log import log as logging
import six

LOG = logging.getLogger('object')


def get_attrname(name):
    """Return the mangled name of the attribute's underlying storage."""
    return '_%s' % name


def make_class_properties(cls):
    # NOTE(danms/comstud): Inherit fields from super classes.
    # mro() returns the current class first and returns 'object' last, so
    # those can be skipped.  Also be careful to not overwrite any fields
    # that already exist.  And make sure each cls has its own copy of
    # fields and that it is not sharing the dict with a super class.
    cls.fields = dict(cls.fields)
    for supercls in cls.mro()[1:-1]:
        if not hasattr(supercls, 'fields'):
            continue
        for name, field in supercls.fields.items():
            if name not in cls.fields:
                cls.fields[name] = field
    for name, typefn in cls.fields.iteritems():

        def getter(self, name=name):
            attrname = get_attrname(name)
            if not hasattr(self, attrname):
                self.obj_load_attr(name)
            return getattr(self, attrname)

        def setter(self, value, name=name, typefn=typefn):
            self._changed_fields.add(name)
            try:
                return setattr(self, get_attrname(name), typefn(value))
            except Exception:
                attr = "%s.%s" % (self.obj_name(), name)
                LOG.exception(_LE('Error setting %(attr)s'),
                              {'attr': attr})
                raise

        setattr(cls, name, property(getter, setter))


class CueObjectMetaclass(type):
    """Metaclass that allows tracking of object classes."""

    # NOTE(danms): This is what controls whether object operations are
    # remoted. If this is not None, use it to remote things over RPC.
    indirection_api = None

    def __init__(cls, names, bases, dict_):
        if not hasattr(cls, '_obj_classes'):
            # This means this is a base class using the metaclass. I.e.,
            # the 'CueObject' class.
            cls._obj_classes = collections.defaultdict(list)
            return

        def _vers_tuple(obj):
            return tuple([int(x) for x in obj.VERSION.split(".")])

        # Add the subclass to CueObject._obj_classes. If the
        # same version already exists, replace it. Otherwise,
        # keep the list with newest version first.
        make_class_properties(cls)


@six.add_metaclass(CueObjectMetaclass)
class CueObject(object):
    """Base class for Cue Objects."""

    fields = {
        'deleted': obj_utils.bool_or_none,
    }

    @classmethod
    def obj_name(cls):
        """Get canonical object name.

        This object name will be used over the wire for remote hydration.

        """
        return cls.__name__

    def __init__(self, **kwargs):
        self._changed_fields = set()
        for key, value in kwargs.items():
            self[key] = value

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, item):
        return getattr(self, item)

    def as_dict(self):
        return dict((k, getattr(self, k))
                for k in self.fields
                if hasattr(self, k))

    def obj_get_changes(self):
        """Returns dict of changed fields and their new values."""
        changes = {}

        for key in self._changed_fields:
            changes[key] = self[key]

        return changes
