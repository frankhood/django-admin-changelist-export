import csv
import datetime
import logging
from io import BytesIO, StringIO
from typing import Any

from django.utils.translation import gettext_lazy
from rest_framework_csv import renderers as csv_renderers

logger = logging.getLogger(__name__)


class ExporterCSVRenderer(csv_renderers.CSVRenderer):
    custom_headers: dict[str, Any] = {}
    csv_delimiter = ";"
    csv_dialect = "excel"
    csv_quotechar = '"'

    def get_custom_headers(self):
        return self.custom_headers

    def write_extra_rows(self, csv_writer):
        # CUSTOM X Inserire righe alla fine
        # csv_writer.writerow([None,None,None,None])
        pass

    def render(self, data, media_type=None, renderer_context=None, writer_opts=None):
        """Render serialized *data* into CSV."""
        if data is None:
            return ""

        if not isinstance(data, list):
            data = [data]

        table = self.tablize(data, labels=self.get_custom_headers())
        csv_buffer = StringIO()
        csv_writer = csv.writer(
            csv_buffer,
            dialect=self.csv_dialect,
            delimiter=self.csv_delimiter,
            quotechar=self.csv_quotechar,
        )
        for row in table:
            csv_writer.writerow([str(elem) for elem in row])
        self.write_extra_rows(csv_writer)
        return csv_buffer.getvalue()


class AdminCSVRenderer(ExporterCSVRenderer):
    """
    Permette di modificare i campi del CSV e la sua formattazione.

        @param custom_headers può essere :
            - None (list_display dell'admin ^ field del model)
            - Lista di field passategli
            - Lista di tuple in cui per ogni chiave viene specificata la sua formattazione
    """


class XLSRenderer(csv_renderers.CSVRenderer):
    """Taken From https://github.com/mjumbewu/django-rest-framework-csv/issues/22."""

    media_type = "application/ms-excel"
    format = "xls"

    def render(
        self, data, media_type=None, renderer_context=None, sheetname="Export", **kwargs
    ):
        try:
            pass

            xls_buffer = BytesIO()  # create a file-like object
            if not isinstance(data, list):
                data = [data]

            header = renderer_context.get("header", self.header)
            labels = renderer_context.get("labels", self.labels)
            table = self.tablize(data, header=header, labels=labels)
            wb = self.to_workbook(table, sheetname=sheetname)
            wb.save(xls_buffer)
            return xls_buffer.getvalue()

        except ImportError:
            logger.error("Cannot Use XLSRenderer if xlwt is not installed!")
            return super().render(
                data, media_type=media_type, renderer_context=renderer_context, **kwargs
            )

    # source: http://fragmentsofcode.wordpress.com/2009/10/09/xlwt-convenience-methods/
    def to_workbook(self, tabular_data, workbook=None, sheetname=None):
        """
        Return the Excel workbook.

        Creating a new workbook if necessary, with the tabular data written to a
        worksheet with the name passed in the 'sheetname' parameter (or a
        default value if sheetname is None or empty).
        """
        import xlwt

        wb = workbook or xlwt.Workbook(encoding="utf8")
        if len(sheetname) > 31:
            sheetname = sheetname[:31]
        ws = wb.add_sheet(sheetname or "Data")
        self.to_worksheet(tabular_data, ws)
        return wb

    def to_worksheet(self, tabular_data, worksheet):
        """
        Write the tabular data to the worksheet (returns None).

        Thanks to John Machin for the tip on using enumerate().
        """
        import xlwt

        default_style = xlwt.Style.default_style
        datetime_style = xlwt.easyxf(num_format_str="dd/mm/yyyy hh:mm")
        date_style = xlwt.easyxf(num_format_str="dd/mm/yyyy")

        for row, rowdata in enumerate(tabular_data):
            worksheet_row = worksheet.row(row)
            for col, val in enumerate(rowdata):
                if isinstance(val, datetime.datetime):
                    val = val.replace(tzinfo=None)
                    style = datetime_style
                elif isinstance(val, datetime.date):
                    style = date_style
                elif isinstance(val, gettext_lazy(val).__class__):
                    # This one is for not resolved django translation labels
                    val = str(val)
                    style = default_style
                else:
                    style = default_style
                worksheet_row.write(col, val, style=style)
