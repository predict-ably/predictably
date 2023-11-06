.. _governance:

==========
Governance
==========

Overview
========

``predictably`` is a consensus-based project that is part of the ``predictably``
community. Anyone with an interest in the project can join the community, contribute
to the project, and participate in the governance process. The rest of this document
describes how that participation takes place, which roles we have in our community,
how we make decisions, and how we acknowledge contributions.

.. note::

    As a new project, ``predictably`` has adopted a provision governance structure.
    We expect this to change as the project grows.

.. _gov_coc:

Code of Conduct
===============

The ``predictably`` project believes that everyone should be able to participate
in our community without fear of harassment or discrimination (see our
:ref:`Code of Conduct guide <coc>`).

Roles
=====

``predictably`` distinguishes between the following key community roles:

- :ref:`Contributors <contribs>`
- :ref:`Core developers <core-devs>`
- :ref:`Steering Committee <steering_committee>`

.. _contribs:

Contributors
------------

Anyone is welcome to contribute to the project. Contributions can take many
forms – not only code – as detailed in the :ref:`contributing guide <how_to_contrib>`

For more details on how we acknowledge contributions,
see the :ref:`acknowledging contributions <acknowledging>` section below.

All of our contributors are listed under the `contributors <contributors.md>`_
section of our documentation.

.. _core-devs:

Core developers
---------------

Core developers are contributors who have shown dedication to project's development
through ongoing engagement with the community (
see the :ref:`core development team <team>`).

The :ref:`core developmer team <team>`  helps ensure the smooth functioning of
the project by:

- ongoing engagement with community
- managing issues and Pull Requests
- closing resolved issues
- reviewing others contributions in accordance with the project
  :ref:`reviewers guide <rev_guide>`)
- approving and merging Pull Requests
- participating in the project's decision making process
- nominating new core developers and steering committee members

Any core developer nominee must receive affirmative votes from two-thirds of
existing core developers over the course of a 5 business day voting period.

Core developers can remain in their role for as long as they like as long as they
continue to perform the role's duties. Core developers who no longer want to
perform the role's duties can resign at any time, while core developers that become
inactive for a 12-month period will move to a "former" core developer status.

.. _steering_committee:

Steering Committee
------------------

Steering Committee (SC) :ref:`team members <team>` are core developers with
additional rights and responsibilities for maintaining the project, including:

- providing technical direction
- strategic planning, roadmapping and project management
- managing community infrastructure (e.g., Github repository, etc)
- fostering collaborations with external organisations
- avoiding deadlocks and ensuring a smooth functioning of the project

SC nominees must be nominated by an existing core developer and receive
affirmative votes from two-thirds of core developers and a simple majority
(with tie breaking) of existing SC members.

Like core developers, SC members who continue to engage with the project
can serve as long as they'd like. However, SC members who do not actively engage
in their SC responsibilities are expected to resign. In the event, a SC member
who no longer engages in their responsibilities does not resign, the remaining
SC members and core developers can vote to remove them (same voting rules
as appointment).

.. _decisions:

Decision making
===============

The ``predictably`` community tries to take viewpoints and feedback from all
community members into account when making decisions in order to arrive at
consensus decisions.

To accomplish this, this section outlines the decision-making process used
by the project.

Where we make decisions
-----------------------

Most of the project's decisions and voting takes place on the project’s `issue
tracker <https://github.com/predict-ably/predictably/issues>`__,
`pull requests <https://github.com/predict-ably/predictably/pulls>`__ or an
:ref:`enhancement proposal <gov_bep>`. However, some sensitive discussions and
all appointment votes occur on private chats.

Core developers are expected to express their consensus (or veto) in the medium
where a given decision takes place. For changes included in the Project's issues
and Pull Requests, this is through comments or Github's built-in review process.

Types of decisions
------------------

The consensus based decision-making process for major types of project
decisions are summarized below.

.. list-table::
   :header-rows: 1

   * - Type of change
     - Decision making process
   * - Code additions or changes
     - :ref:`Lazy consensus <lazy>`
   * - Documentation changes
     - :ref:`Lazy consensus <lazy>`
   * - Changes to the API design, hard dependencies, or supported versions
     - :ref:`Lazy consensus <lazy>` based on an :ref:`PREP <gov_bep>`
   * - Changes to predictably's governance
     - :ref:`Lazy consensus <lazy>` based on an :ref:`PREP <gov_bep>`
   * - Appointment to core developer or steering committee status
     - Anonymous voting on slack


How we make decisions
---------------------

.. _lazy:

Lazy consensus
^^^^^^^^^^^^^^

Changes are approved "lazily" when after *reasonable* amount of time
the change receives approval from at least one core developer
and no rejections from any core developers.

This is approach is designed to make it easier to add new features and make changes
to the project as it develops. To make sure things run smoothly,
:ref:`core developers <core-devs>` should make sure that the *reasonable* time
other community members have to provide feedback on the changes is commensurate
to the scope of the change. For changes to the API or other larger changes,
core developers should actively solicit feedback from their peers.

.. _gov_bep:

``predictably`` enhancement proposals
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Project design decisions have a more detailed approval process,
commensurate with their broader impact on the project. Any changes
to the project's core API design, hard dependencies or supported versions
should first be presented in a ``predictably`` enhancement proposal (PREP).

See the developer guide for more information on creating a :ref:`PREP <bep>`.

Resolving conflicts
^^^^^^^^^^^^^^^^^^^

When consensus can't be found lazily, the project's core developers will vote
to decide how to proceed on an issue. Any core developers can call for a vote
on a topic. A topic must receive two-thirds of core developer votes cast
(abstentions are allowed) via comments on the relevant issue or
Pull Request over a 5 day voting period.

In the event a proposed change does not gather the necesssary votes, then:

- The core developer who triggered the vote can choose to drop the issue
- The proposed changes can be escalated to the SC, who will seek to learn more
  about the team member viewpoints, before bringing the topic up for a simple
  majority vote of SC members.

.. _acknowledging:

Acknowledging contributions
===========================

The ``predictably`` project values all kinds of contributions and the
development team is committed to recognising each of them fairly.

The project follows the `all-contributors <https://allcontributors.org>`_
specification to recognise all contributors, including those that don’t
contribute code. Please see our list of `all contributors <contributors.md>`_.

Please let us know or open a PR with the appropriate changes to
`predictably/.all-contributorsrc
<https://github.com/predict-ably/predictably/blob/main/.all-contributorsrc>`_
if we have missed anything.

.. note::

  ``predictably`` is an open-source project. All code is contributed
  under `our open-source
  license <https://github.com/sktime/baseobject/blob/main/LICENSE>`_.
  Contributors acknowledge that they have rights to make their contribution
  (code or otherwise) available under this license.

Outlook
=======

As with other parts of the project, the governance may change as the project
matures. Suggestions on potential governance changes are also welcome.

References
==========

Our governance model is inspired by various existing governance
structures. In particular, we'd like to acknowledge:

* `sktime's governance model <https://www.sktime.org/en/latest/get_involved/governance.htmls>`_
* `scikit-learn's governance model <https://scikit-learn.org/stable/governance.html>`_
