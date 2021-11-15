=====
Usage
=====

To use Django Admin Changelist Export in a project, add it to your `INSTALLED_APPS`:

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
