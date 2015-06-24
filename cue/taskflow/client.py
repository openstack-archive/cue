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
import contextlib
import uuid

from oslo_config import cfg
from oslo_utils import uuidutils
from six.moves import urllib_parse
import taskflow.engines as engines
import taskflow.jobs.backends as job_backends
import taskflow.persistence.backends as persistence_backends
import taskflow.persistence.logbook as logbook


def _make_conf(backend_uri):
    """A helper function for generating persistence backend configuration.

    This function takes a backend configuration as a URI of the form
    <backend type>://<backend host>/<path>.

    :param backend_uri: URI for backend connection
    :return: A configuration dictionary for use with
             taskflow.persistence.backends
    """
    parsed_url = urllib_parse.urlparse(backend_uri)
    backend_type = parsed_url.scheme.lower()
    if not backend_type:
        raise ValueError("Unknown backend type for uri: %s" % (backend_type))
    if backend_type in ('file', 'dir'):
        conf = {
            'path': parsed_url.path,
            'connection': backend_uri,
        }
    elif backend_type in ('zookeeper',):
        conf = {
            'path': parsed_url.path,
            'hosts': parsed_url.netloc,
            'connection': backend_uri,
        }
    else:
        conf = {
            'connection': backend_uri,
        }
    return conf

_task_flow_client = None


def get_client_instance(client_name=None, persistence=None, jobboard=None):
    """Create and access a single instance of TaskFlow client

    :param client_name: Name of the client interacting with the jobboard
    :param persistence: A persistence backend instance to be used in lieu
                        of auto-creating a backend instance based on
                        configuration parameters
    :param jobboard: A jobboard backend instance to be used in lieu of
                     auto-creating a backend instance based on
                     configuration parameters
    :return: A :class:`.Client` instance.
    """
    global _task_flow_client

    if _task_flow_client is None:
        if persistence is None:
            persistence = create_persistence()
        if jobboard is None:
            jobboard = create_jobboard(persistence=persistence)
        if client_name is None:
            client_name = "cue_job_client"

        _task_flow_client = Client(client_name,
                                   persistence=persistence,
                                   jobboard=jobboard)

    return _task_flow_client


def create_persistence(conf=None, **kwargs):
    """Factory method for creating a persistence backend instance

    :param conf: Configuration parameters for the persistence backend.  If
                 no conf is provided, zookeeper configuration parameters
                 for the job backend will be used to configure the
                 persistence backend.
    :param kwargs: Keyword arguments to be passed forward to the
                   persistence backend constructor
    :return: A persistence backend instance.
    """
    if conf is None:
        connection = cfg.CONF.taskflow.persistence_connection
        if connection is None:
            connection = ("zookeeper://%s/%s"
                          % (
                              cfg.CONF.taskflow.zk_hosts,
                              cfg.CONF.taskflow.zk_path,
                            ))
        conf = _make_conf(connection)
    be = persistence_backends.fetch(conf=conf, **kwargs)
    with contextlib.closing(be.get_connection()) as conn:
        conn.upgrade()
    return be


def create_jobboard(board_name=None, conf=None, persistence=None, **kwargs):
    """Factory method for creating a jobboard backend instance

    :param board_name: Name of the jobboard
    :param conf: Configuration parameters for the jobboard backend.
    :param persistence: A persistence backend instance to be used with the
                        jobboard.
    :param kwargs: Keyword arguments to be passed forward to the
                   persistence backend constructor
    :return: A persistence backend instance.
    """
    if board_name is None:
        board_name = cfg.CONF.taskflow.jobboard_name

    if conf is None:
        conf = {'board': 'zookeeper'}

        conf.update({
            "path": "%s/jobs" % (cfg.CONF.taskflow.zk_path),
            "hosts": cfg.CONF.taskflow.zk_hosts,
            "timeout": cfg.CONF.taskflow.zk_timeout
        })

    jb = job_backends.fetch(
            name=board_name,
            conf=conf,
            persistence=persistence,
            **kwargs)
    jb.connect()
    return jb


class Client(object):
    """An abstraction for interacting with Taskflow

    This class provides an abstraction for Taskflow to expose a simpler
    interface for posting jobs to Taskflow Jobboards than what is provided
    out of the box with Taskflow.

    TODO(sputnik13): persistence and jobboard should ideally be closed during
                     __del__ but that seems to throw exceptions even though it
                     doesn't seem like it should...  this should be
                     investigated further

    :ivar persistence: persistence backend instance
    :ivar jobboard: jobboard backend instance
    """

    def __init__(self, client_name, board_name=None, persistence=None,
                 jobboard=None, **kwargs):
        """Constructor for Client class

        :param client_name: Name of the client interacting with the jobboard
        :param board_name: Name of the jobboard
        :param persistence: A persistence backend instance to be used in lieu
                            of auto-creating a backend instance based on
                            configuration parameters
        :param jobboard: A jobboard backend instance to be used in lieu of
                         auto-creating a backend instance based on
                         configuration parameters
        :param kwargs: Any keyword arguments to be passed forward to
                       persistence and job backend constructors
        """
        super(Client, self).__init__()

        if jobboard is None and board_name is None:
            raise AttributeError("board_name must be supplied "
                                 "if a jobboard is None")

        self._client_name = client_name

        self.persistence = persistence or create_persistence(**kwargs)

        self.jobboard = jobboard or create_jobboard(board_name,
                                                    None,
                                                    self.persistence,
                                                    **kwargs)

    @classmethod
    def create(cls, client_name, board_name=None, persistence=None,
               jobboard=None, **kwargs):
        """Factory method for creating a Client instance

        :param client_name: Name of the client interacting with the jobboard
        :param board_name: Name of the jobboard
        :param persistence: A persistence backend instance to be used in lieu
                            of auto-creating a backend instance based on
                            configuration parameters
        :param jobboard: A jobboard backend instance to be used in lieu of
                         auto-creating a backend instance based on
                         configuration parameters
        :param kwargs: Any keyword arguments to be passed forward to
                       persistence and job backend constructors
        :return: A :class:`.Client` instance.
        """
        return cls(client_name, board_name=board_name, persistence=persistence,
                   jobboard=jobboard, **kwargs)

    def post(self, flow_factory, job_args=None,
             flow_args=None, flow_kwargs=None, tx_uuid=None):
        """Method for posting a new job to the jobboard

        :param flow_factory: Flow factory function for creating a flow instance
                             that will be executed as part of the job.
        :param job_args: 'store' arguments to be supplied to the engine
                         executing the flow for the job
        :param flow_args: Positional arguments to be passed to the flow factory
                          function
        :param flow_kwargs: Keyword arguments to be passed to the flow factory
                            function
        :param tx_uuid: Transaction UUID which will be injected as 'tx_uuid' in
                        job_args.  A tx_uuid will be generated if one is not
                        provided as an argument.
        :return: A taskflow.job.Job instance that represents the job that was
                 posted.
        """
        if isinstance(job_args, dict) and 'tx_uuid' in job_args:
            raise AttributeError("tx_uuid needs to be provided as an argument"
                                 "to Client.post, not as a member of job_args")

        if tx_uuid is None:
            tx_uuid = uuidutils.generate_uuid()

        job_name = "%s[%s]" % (flow_factory.__name__, tx_uuid)
        book = logbook.LogBook(job_name, uuid=tx_uuid)

        if flow_factory is not None:
            flow_detail = logbook.FlowDetail(job_name, str(uuid.uuid4()))
            book.add(flow_detail)

        job_details = {'store': job_args or {}}
        job_details['store'].update({
            'tx_uuid': tx_uuid
        })
        job_details['flow_uuid'] = flow_detail.uuid

        self.persistence.get_connection().save_logbook(book)

        engines.save_factory_details(
            flow_detail, flow_factory, flow_args, flow_kwargs,
            self.persistence)

        job = self.jobboard.post(job_name, book, details=job_details)
        return job

    def joblist(self, only_unclaimed=False, ensure_fresh=False):
        """Method for retrieving a list of jobs in the jobboard

        :param only_unclaimed: Return only unclaimed jobs
        :param ensure_fresh: Return only the most recent jobs available.
                             Behavior of this parameter is backend specific.
        :return: A list of jobs in the jobboard
        """
        return list(self.jobboard.iterjobs(only_unclaimed=only_unclaimed,
                                            ensure_fresh=ensure_fresh))

    def delete(self, job=None, job_id=None):
        """Method for deleting a job from the jobboard.

        Due to constraints in the available taskflow interfaces, deleting by
        job_id entails retrieving and iterating over the list of all jobs in
        the jobboard.  Thus deleting by job rather than job_id can be faster.

        :param job: A Taskflow.job.Job representing the job to be deleted
        :param job_id: Unique job_id referencing the job to be deleted
        :return:
        """
        if (job is None) == (job_id is None):
            raise AttributeError("exactly one of either job or job_id must "
                                 "be supplied")

        if job is None:
            for j in self.joblist():
                if j.uuid == job_id:
                    job = j

        self.jobboard.claim(job, self._client_name)
        self.jobboard.consume(job, self._client_name)