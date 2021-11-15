import logging

import django
from django.utils import formats, timezone
from django.views import View
from drf_renderer_xlsx.renderers import XLSXRenderer
from rest_framework import generics, serializers
from rest_framework.utils import model_meta

from .csv_utils import APIFileNameMixin
from rest_framework_csv import renderers as csv_renderers

from .renderers import XLSRenderer

logger = logging.getLogger(__name__)

jquery_compatibility = django.get_version() < "1.7"

__all__ = [
    "ChangelistExporterModelAdminMixin",
]


class ChangelistExporterModelAdminMixin(object):
    """
    Add actions to your admin for exporting changelist in csv, xls and xlsx format.

    Serializer can be passed or default created.
    View can be passed or inline created.
    Minimum steps are:
        - Defining file_name with relative extension
        - Queryset (given by change_list)
        - Fields to write (list_display's fields by default)
    """

    actions = ["export_data_in_csv", "export_data_in_xls", "export_data_in_xlsx"]
    csv_exporter_view: View = None
    xls_exporter_view: View = None
    xlsx_exporter_view: View = None
    csv_filename = None
    xls_filename = None
    xlsx_filename = None
    csv_delimiter = ";"
    csv_dialect = "excel"
    csv_quotechar = '"'

    def get_csv_filename(self):
        return self.csv_filename or "{0}_export_{1}.csv".format(
            self.model.__name__.lower(), formats.date_format(timezone.now(), "Ymd_Hi")
        )

    def get_xls_filename(self):
        return self.xls_filename or "{0}_export_{1}.xls".format(
            self.model.__name__.lower(), formats.date_format(timezone.now(), "Ymd_Hi")
        )

    def get_xlsx_filename(self):
        return self.xlsx_filename or "{0}_export_{1}.xlsx".format(
            self.model.__name__.lower(), formats.date_format(timezone.now(), "Ymd_Hi")
        )

    def get_csv_list_display(self):
        if self.csv_exporter_view:
            return self.get_csv_exporter_view().serializer_class.Meta.fields
        return tuple(self.list_display)

    def get_csv_list_fields(self):
        return self.get_csv_list_display()

    def get_csv_field_label(self, field_name):
        field_label = field_name
        model_class = self.model
        model_info = model_meta.get_field_info(model_class)
        try:
            if hasattr(self, field_name):
                try:
                    field_label = getattr(self, field_name).short_description
                    logger.debug("{0} -> {1}".format(field_name, field_label))
                except AttributeError:
                    field_label = field_name
                    logger.warning(
                        "{0} -> {1} (Setta la short description per visualizzare bene questo field_label)".format(
                            field_name, field_label
                        )
                    )
            elif field_name in model_info.fields_and_pk:
                field_label = model_class._meta.get_field(field_name).verbose_name
                logger.debug("{0} -> {1}".format(field_name, field_label))
            elif field_name in model_info.relations:
                field_label = model_class._meta.get_field(field_name).verbose_name
                # ===========================================================
                # nel caso di 2 FK allo stesso modello non se ne esce, è utile prendere il verbose_name che di default però è la slug del modello associato
                # relation_info = model_info.relations[field_name]
                # print("relation_info : {0}".format(relation_info))
                # if relation_info.to_many:
                #     field_label = relation_info.related_model._meta.verbose_name_plural
                # else:
                #     field_label = relation_info.related_model._meta.verbose_name
                # ===========================================================
                logger.debug("{0} -> {1}".format(field_name, field_label))
            elif hasattr(model_class, field_name):
                try:
                    field_label = getattr(model_class, field_name).short_description
                    logger.debug("{0} -> {1}".format(field_name, field_label))
                except AttributeError:
                    field_label = field_name
                    logger.warning(
                        "{0} -> {1} (Setta la short description per visualizzare bene questo field_label)".format(
                            field_name, field_label
                        )
                    )

        except Exception:
            logger.exception("Cannot find label for field {0}".format(field_name))
        return field_label

    def get_csv_exporter_view(self):
        csv_exporter_view = self.csv_exporter_view
        if csv_exporter_view is not None:
            return csv_exporter_view

        assert self.model is not None, (
            "'%s' should either include a 'csvexporter_view' attribute, "
            "or use the 'model' attribute as a shortcut for "
            "automatically generating a csv exporter class." % self.__class__.__name__
        )

        class _AdminCSVSerializer(serializers.ModelSerializer):
            model_admin = self

            class Meta:
                model = self.model
                fields = self.get_csv_list_fields()

            @staticmethod
            def get_headers_labels():
                return []

            def factory_admin_function(self, field_name, model_admin):
                def admin_function(obj):
                    return getattr(model_admin, field_name)(obj)

                return admin_function

            def factory_relational_function(self, field_name, relation_info):
                def relation_function(obj):
                    return getattr(obj, field_name).__str__() or ""

                return relation_function

            def build_admin_field(self, field_name, model_class):
                field_class = serializers.SerializerMethodField
                field_kwargs = {}
                setattr(
                    self,
                    "get_{field_name}".format(field_name=field_name),
                    self.factory_admin_function(field_name, self.model_admin),
                )
                return field_class, field_kwargs

            def build_unknown_field(self, field_name, model_class):
                if hasattr(self.model_admin, field_name):
                    return self.build_admin_field(field_name, model_class)
                return super(_AdminCSVSerializer, self).build_unknown_field(
                    field_name, model_class
                )

            def build_relational_field(self, field_name, relation_info):
                """Create fields for forward and reverse relationships."""
                if not relation_info.to_many:
                    field_class = serializers.SerializerMethodField
                    field_kwargs = {}
                    setattr(
                        self,
                        "get_{field_name}".format(field_name=field_name),
                        self.factory_relational_function(field_name, relation_info),
                    )
                    return field_class, field_kwargs
                else:
                    return super(_AdminCSVSerializer, self).build_relational_field(
                        field_name, relation_info
                    )

        class DefaultCSVExporterView(APIFileNameMixin, generics.ListAPIView):
            model = self.model
            renderer_classes = (csv_renderers.CSVRenderer,)
            serializer_class = _AdminCSVSerializer
            file_name = self.get_csv_filename()
            custom_headers = [
                (x, self.get_csv_field_label(x)) for x in self.get_csv_list_display()
            ]

            def get_file_name(self):
                return self.file_name

            def post(self, *args, **kwargs):
                return self.get(*args, **kwargs)

            def get_renderer_context(self):
                context = super().get_renderer_context()
                context.update({
                    'labels': dict(self.custom_headers)
                })
                return context

        return DefaultCSVExporterView

    def get_xls_exporter_view(self):

        xls_exporter_view = self.xls_exporter_view
        if xls_exporter_view is not None:
            return xls_exporter_view
        class _AdminXLSRenderer(XLSRenderer):
            custom_headers = [
                (x, str(self.get_csv_field_label(x)))
                for x in self.get_csv_list_display()
            ]

        DefaultXLSExporterView = self.get_csv_exporter_view()
        DefaultXLSExporterView.renderer_classes = (_AdminXLSRenderer,)
        DefaultXLSExporterView.file_name = self.get_xls_filename()

        return DefaultXLSExporterView

    def get_xlsx_exporter_view(self):

        xlsx_exporter_view = self.xlsx_exporter_view
        if xlsx_exporter_view is not None:
            return xlsx_exporter_view
        print('obada')
        DefaultXLSExporterView = self.get_csv_exporter_view()
        DefaultXLSExporterView.renderer_classes = (XLSXRenderer,)
        DefaultXLSExporterView.file_name = self.get_xlsx_filename()

        return DefaultXLSExporterView

    def export_data_in_csv(self, request, queryset):
        csv_exporter_view = self.get_csv_exporter_view()
        request.method = "GET"
        return csv_exporter_view.as_view(queryset=queryset, model=queryset.model)(
            request=request
        )

    export_data_in_csv.short_description = "Esporta dati in formato .csv"  # type: ignore

    def export_data_in_xls(self, request, queryset):
        xls_exporter_view = self.get_xls_exporter_view()
        request.method = "GET"
        return xls_exporter_view.as_view(
            queryset=queryset,
            model=queryset.model,
        )(request=request)

    export_data_in_xls.short_description = "Esporta dati in formato .xls"  # type: ignore

    def export_data_in_xlsx(self, request, queryset):
        xlsx_exporter_view = self.get_xlsx_exporter_view()
        request.method = "GET"
        return xlsx_exporter_view.as_view(
            queryset=queryset,
            model=queryset.model,
        )(request=request)

    export_data_in_xlsx.short_description = "Esporta dati in formato .xlsx"  # type: ignore
