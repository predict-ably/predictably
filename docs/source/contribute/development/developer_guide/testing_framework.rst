=================
Testing Framework
=================

.. note::

    This page will explain ``predictably``'s testing framework with an emphasis on
    how contributors should use the framework to test their contributions. It is
    a work in progress.

``predictably`` uses ``pytest`` to verify code is working as expected.
This page gives an overview of the tests, an introduction on adding new tests,
and how to extend the testing framework.

.. warning::

  This page is under construction. We plan to add more tests and increased
  documentation on the testing framework in an upcoming release.

Test module architecture
========================

``predictably`` uses a tiered approach to test its functionality:

- *package level* tests are located in ``predictably/tests/`` and are meant to
  test functionality used throughout the package.

- *module level* tests are included in the ``tests`` folders in each module and
   are focused on verifying an individual models functionality.

- *low level* tests in the ``tests`` folders in each module are used to verify the
  functionality of individual code artifacts

Module conventions are as follows:

* Each module contains a ``tests`` folder that contains tests specific to that module.
    * Sub-modules may also contain ``tests`` folders.
    * *module* tests focused on testing a specific class interface should contain a file
      ``test_all_[name_of_class].py``
* ``tests`` folders may contain ``_config.py`` files to collect test
  configuration settings for that modules.
* *module* and *low* level tests should not repeat tests performed at a higher level.
