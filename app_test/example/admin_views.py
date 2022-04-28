from django.contrib.auth import get_user_model
from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer
from rest_framework import generics
from rest_framework_csv import renderers as csv_renderers

from admin_changelist_export.csv_utils import APIFileNameMixin
from admin_changelist_export.renderers import XLSRenderer
from app_test.example.serializers import UserExportSerializer


class UserXLSXExporterView(APIFileNameMixin, XLSXFileMixin, generics.ListAPIView):
    renderer_classes = (XLSXRenderer,)
    model = get_user_model()
    serializer_class = UserExportSerializer
    file_name = "export_users.xlsx"

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get_file_name(self):
        return self.file_name

    def get_column_header(self):
        return {
            "titles": self.serializer_class.get_custom_labels(),
        }


class UserXLSExporterView(APIFileNameMixin, generics.ListAPIView):
    renderer_classes = (XLSRenderer,)
    model = get_user_model()
    serializer_class = UserExportSerializer
    file_name = "export_users.xls"

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get_file_name(self):
        return self.file_name

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context.update({"labels": self.serializer_class.get_headers_labels()})
        return context


class UserCSVExporterView(APIFileNameMixin, generics.ListAPIView):
    model = get_user_model()
    renderer_classes = (csv_renderers.CSVRenderer,)
    serializer_class = UserExportSerializer
    file_name = "export_users.csv"

    def get_file_name(self):
        return self.file_name

    def post(self, *args, **kwargs):
        response = self.get(*args, **kwargs)
        return response

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context.update({"labels": self.serializer_class.get_headers_labels()})
        return context
