================
Getting Involved
================

#openstack-cue
--------------
There is an active IRC channel at irc://freenode.net/#openstack-cue, where many of the cue contributors can be found, as
well as users from various organisations.

Weekly meetings
---------------
There is a weekly irc meet. The agenda and other details are listed at
`Cue meetings wiki page`_. Currently the meeting is
held every Wednesday at 18:00-19:00 UTC on the IRC channel irc://freenode.net/#openstack-meeting-alt


Contributing
------------
We welcome fixes, extensions, documentation, pretty much anything that helps improve Cue, contributing is easy & follows
the standard OpenStack `Gerrit workflow`_, if you're looking for something to do, you could always checkout the blueprint_ & bug_
lists.

Assuming you've already got a working :ref:`Development Environment`, here's a quick summary:

Install the git-review package to make life easier

.. code-block:: shell-session

  pip install git-review

Branch, work, & submit:

.. code-block:: shell-session

  # cut a new branch, tracking master
  git checkout --track -b bug/id origin/master
  # work work work
  git add stuff
  git commit
  # rebase/squash to a single commit before submitting
  git rebase -i
  # submit
  git-review

Coding Standards
----------------
Cue uses the OpenStack flake8 coding standards guidelines.
These are stricter than pep8, and are run by gerrit on every commit.

You can use tox to check your code locally by running

.. code-block:: shell-session

  # For just flake8 tests
  tox -e flake8
  # For tests + flake8
  tox

.. _Gerrit workflow: http://docs.openstack.org/infra/manual/developers.html#development-workflow
.. _blueprint: https://blueprints.launchpad.net/cue
.. _bug: https://bugs.launchpad.net/cue
.. _Cue meetings wiki page: https://wiki.openstack.org/wiki/Meetings/Cue
