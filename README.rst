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
        'admin_changelist_export',
        ...
    )

Add ChangelistExporterModelAdminMixin to your Admin, with actions and views (if you need a custom export):

.. code-block:: python

    class CustomUserAdmin(ChangelistExporterModelAdminMixin, DjangoUserAdmin):
    actions = ["export_data_in_csv", "export_data_in_xls", "export_data_in_xlsx"]
    csv_exporter_view = UserCSVExporterView
    xls_exporter_view = UserXLSExporterView
    xlsx_exporter_view = UserXLSXExporterView


    admin.site.unregister(get_user_model())
    admin.site.register(get_user_model(), CustomUserAdmin)

You can only add the mixin if you need only to download "AS-IS" changelist admin columns

Features
--------

* Can easily download changelist fields in .csv, .xls and .xlsx extensions.
* Can add to an admin model views to customize its download.

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
