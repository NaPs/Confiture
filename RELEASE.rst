===========================
Confiture release procedure
===========================

Release procedure::

    [ ] Remove the ~dev in setup.py version
    [ ] Remove the ~dev in docs/conf.py version
    [ ] Update the changelog in README.rst to add release date
    [ ] Commit changes on setup.py, docs/conf.py and README.rst with
        the following message:
        > Released version {version}
    [ ] Tag the latest commit with the following message:
        > Confiture v{version}
    [ ] Send the update en PYPI: setup.py sdist bdist_egg upload
    [ ] Increment number and add ~dev in setup.py version
    [ ] Increment number and add ~dev in docs/conf.py version
    [ ] Update the changelog in README.rst to add the new development version:
        > v{new_version} (not yet released)
        > ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        >
        > -
    [ ] Commit changes on setup.py, docs/conf.py and README.rst with the
        following message:
        > Started development on {new_version}~dev
    [ ] Push commits on all remotes.
    [ ] Update the doc on read the docs
