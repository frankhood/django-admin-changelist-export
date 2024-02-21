import codecs
import csv
import logging
from io import StringIO

logger = logging.getLogger(__name__)


class CsvUnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        """
        CSV writer.

        Which will write rows to CSV file "f", which is encoded in the given encoding.
        """
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def cast_to_str(self, obj):
        if isinstance(obj, str):
            return str(obj)
        elif hasattr(obj, "__str__"):
            return str(obj)
        else:
            raise TypeError(
                "Expecting unicode, str, or object castable"
                " to unicode or string, got: %r" % type(obj)
            )

    def writerow(self, row):
        self.writer.writerow([self.cast_to_str(s) for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class UTF8Recoder:
    def __init__(self, f, encoding):
        """Read an encoded stream and reencodes the input to UTF-8."""
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class CsvUnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwargs):
        """CSV reader which will iterate over lines in the CSV file "f", which is encoded in the given encoding."""
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwargs)

    def next(self):
        row = next(self.reader)
        return [str(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class APIFileNameMixin:
    file_name: str = ""

    def get_file_name(self):
        return self.file_name

    def get(self, *args, **kwargs):
        resp = super().get(*args, **kwargs)
        file_name = self.get_file_name()
        if file_name:
            resp["Content-Disposition"] = 'attachment; filename="%s"' % file_name
        setattr(resp.data, "header", self.serializer_class.get_headers_labels())
        return resp
