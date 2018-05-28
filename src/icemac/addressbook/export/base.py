import zope.interface
import icemac.addressbook.export.interfaces


@zope.interface.implementer(icemac.addressbook.export.interfaces.IExporter)
class BaseExporter(object):
    """Abstract base for exporters which defines some convenience methods."""

    # to be set in subclass
    file_extension = NotImplemented
    mime_type = NotImplemented

    def __init__(self, persons, request=None):
        self.persons = persons
        self.request = request

    def export(self):
        raise NotImplementedError()
