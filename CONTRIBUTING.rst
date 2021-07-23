Contributing Guidelines
=======================

Questions, Feature Requests, Bug Reports, and Feedback. . .
-----------------------------------------------------------

…should all be reported on the `Github Issue Tracker`_ .

.. _`Github Issue Tracker`: https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues?state=open

Setting Up for Local Development
--------------------------------

1. Fork marshmallow-sqlalchemy_ on Github.

::

    $ git clone https://github.com/marshmallow-code/marshmallow-sqlalchemy.git
    $ cd marshmallow-sqlalchemy

2. Install development requirements. **It is highly recommended that you use a virtualenv.**
   Use the following command to install an editable version of
   marshmallow-sqlalchemy along with its development requirements.

::

    # After activating your virtualenv
    $ pip install -e '.[dev]'

3. Install the pre-commit hooks, which will format and lint your git staged files.

::

    # The pre-commit CLI was installed above
    $ pre-commit install --allow-missing-config

Git Branch Structure
--------------------

marshmallow-sqlalchemy abides by the following branching model:

``dev``
    Current development branch. **New features should branch off here**.

``X.Y-line``
    Maintenance branch for release ``X.Y``. **Bug fixes should be sent to the most recent release branch.**. The maintainer will forward-port the fix to ``dev``. Note: exceptions may be made for bug fixes that introduce large code changes.

**Always make a new branch for your work**, no matter how small. Also, **do not put unrelated changes in the same branch or pull request**. This makes it more difficult to merge your changes.

Pull Requests
--------------

1. Create a new local branch.
::

    # For a new feature
    $ git checkout -b name-of-feature dev

    # For a bugfix
    $ git checkout -b fix-something 1.2-line

2. Commit your changes. Write `good commit messages <http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>`_.
::

    $ git commit -m "Detailed commit message"
    $ git push origin name-of-feature

3. Before submitting a pull request, check the following:

- If the pull request adds functionality, it is tested and the docs are updated.
- You've added yourself to ``AUTHORS.rst``.

4. Submit a pull request to ``marshmallow-code:dev`` or the appropriate maintenance branch.
   The `CI <https://dev.azure.com/sloria/sloria/_build/latest?definitionId=10&branchName=dev>`_ build
   must be passing before your pull request is merged.

Running Tests
-------------

To run all To run all tests: ::

    $ pytest

To run formatting and syntax checks: ::

    $ tox -e lint

(Optional) To run tests in all supported Python versions in their own virtual environments (must have each interpreter installed): ::

    $ tox

Documentation
-------------

Contributions to the documentation are welcome. Documentation is written in `reStructuredText`_ (rST). A quick rST reference can be found `here <https://docutils.sourceforge.io/docs/user/rst/quickref.html>`_. Builds are powered by Sphinx_.

To build the docs in "watch" mode: ::

   $ tox -e watch-docs

Changes in the `docs/` directory will automatically trigger a rebuild.


.. _Sphinx: https://www.sphinx-doc.org/
.. _`reStructuredText`: https://docutils.sourceforge.io/rst.html

.. _`marshmallow-sqlalchemy`: https://github.com/marshmallow-code/marshmallow-sqlalchemy
