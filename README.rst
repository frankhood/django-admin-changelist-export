=============================
Django Admin Changelist Export
=============================

.. image:: https://badge.fury.io/py/django-admin-changelist-export.svg
    :target: https://badge.fury.io/py/django-admin-changelist-export

.. image:: https://travis-ci.org/frankhood/django-admin-changelist-export.svg?branch=master
    :target: https://travis-ci.org/frankhood/django-admin-changelist-export

.. image:: https://codecov.io/gh/frankhood/django-admin-changelist-export/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/frankhood/django-admin-changelist-export

Your project description goes here

Documentation
-------------

The full documentation is at https://django-admin-changelist-export.readthedocs.io.

Quickstart
----------

Install Django Admin Changelist Export::

    pip install django-admin-changelist-export

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'admin_changelist_export.apps.AdminChangelistExportConfig',
        ...
    )

Add Django Admin Changelist Export's URL patterns:

.. code-block:: python

    from admin_changelist_export import urls as admin_changelist_export_urls


    urlpatterns = [
        ...
        url(r'^', include(admin_changelist_export_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox


Development commands
---------------------

::

    pip install -r requirements_dev.txt
    invoke -l


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
