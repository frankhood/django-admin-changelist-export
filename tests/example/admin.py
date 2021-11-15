from django.contrib import admin
from django.contrib.auth import get_user_model

from admin_changelist_export.mixins import ChangelistExporterModelAdminMixin
from tests.example.admin_views import UserCSVExporterView, UserXLSExporterView, UserXLSXExporterView
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin


class CustomUserAdmin(ChangelistExporterModelAdminMixin, DjangoUserAdmin):
    actions = ["export_data_in_csv", "export_data_in_xls", "export_data_in_xlsx"]
    csv_exporter_view = UserCSVExporterView
    xls_exporter_view = UserXLSExporterView
    xlsx_exporter_view = UserXLSXExporterView


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), CustomUserAdmin)
