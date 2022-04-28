from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from admin_changelist_export.mixins import ChangelistExporterModelAdminMixin
from app_test.example import admin_views


class CustomUserAdmin(ChangelistExporterModelAdminMixin, DjangoUserAdmin):
    actions = ["export_data_in_csv", "export_data_in_xls", "export_data_in_xlsx"]
    csv_exporter_view = admin_views.UserCSVExporterView
    xls_exporter_view = admin_views.UserXLSExporterView
    xlsx_exporter_view = admin_views.UserXLSXExporterView


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), CustomUserAdmin)
