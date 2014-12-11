#    Copyright 2014 Rackspace
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
#
# Copied from Octavia

from cue.common import exception
from cue.db.sqlalchemy import types

import uuid

from oslo.db.sqlalchemy import models
from oslo.utils import timeutils
import sqlalchemy as sa
from sqlalchemy.ext import declarative


class CueBase(models.ModelBase):
    @classmethod
    def create(cls, session, **kwargs):
        with session.begin():
            instance = cls(**kwargs)
            session.add(instance)
        return instance

    @classmethod
    def delete(cls, session, id):
        model = session.query(cls).filter_by(id=id).first()
        if not model:
            raise exception.NotFound
        with session.begin():
            session.delete(model)
            session.flush()

    @classmethod
    def delete_batch(self, session, ids=None):
        [self.delete(session, id) for id in ids]

    @classmethod
    def update(cls, session, id, **kwargs):
        with session.begin():
            kwargs.update(updated_at=timeutils.utcnow())
            session.query(cls).filter_by(id=id).update(kwargs)

    @classmethod
    def get(cls, session, **filters):
        instance = session.query(cls).filter_by(**filters).first()
        if not instance:
            raise exception.NotFound
        return instance

    @classmethod
    def get_all(cls, session, **filters):
        data = session.query(cls).filter_by(**filters).all()
        return data

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = self[c.name]
        return d


class LookupTableMixin(object):
    """Mixin to add to classes that are lookup tables."""
    name = sa.Column(sa.String(255), primary_key=True, nullable=False)
    description = sa.Column(sa.String(255), nullable=True)


class IdMixin(object):
    """Id mixin, add to subclasses that have a tenant."""
    id = sa.Column(types.UUID(), nullable=False,
                   default=lambda i: str(uuid.uuid4()),
                   primary_key=True)


class ProjectMixin(object):
    """Project mixin, add to subclasses that have a project."""
    project_id = sa.Column(sa.String(36))


class TimeMixin(object):
    created_at = sa.Column('created_at', sa.DateTime(),
                           default=timeutils.utcnow(), nullable=False)
    updated_at = sa.Column('updated_at', sa.DateTime(),
                           default=timeutils.utcnow(), nullable=False)
    deleted_at = sa.Column('deleted_at', sa.DateTime(),
                           nullable=True)

BASE = declarative.declarative_base(cls=CueBase)
