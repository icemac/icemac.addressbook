# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
import ZODB.blob
import icemac.addressbook.entities
import icemac.addressbook.file.interfaces
import icemac.addressbook.interfaces
import persistent
import zope.container.contained
import zope.interface


@zope.interface.implementer(icemac.addressbook.file.interfaces.IFile)
class BaseFile(persistent.Persistent, zope.container.contained.Contained):
    """Base class for a file."""

    zope.schema.fieldproperty.createFieldProperties(
        icemac.addressbook.file.interfaces.IFile, omit=['data', 'size'])

    def __init__(self, data='', *args, **kw):
        super(BaseFile, self).__init__(*args, **kw)
        # initialize blob with no data
        self._data = ZODB.blob.Blob()
        self.data = data

    @property
    def size(self):
        reader = self.open()
        reader.seek(0, 2)
        size = int(reader.tell())
        reader.close()
        return size

    @property
    def data(self):
        # This method can't be used to read the data, use openDetached instead.
        # This is necessary because of the stupidity of z3c.form which reads
        # the whole file when rendering a form.
        return ''

    @data.setter
    def data(self, data):
        with self.open('w') as fp:
            fp.write(data)

    def replace(self, filename):
        """Replace with another file."""
        self._data.consumeFile(filename)

    def openDetached(self, mode='r'):
        return open(self._data.committed(), 'rb')

    def open(self, mode='r'):
        return self._data.open(mode)


@zope.interface.implementer(
    icemac.addressbook.interfaces.IPersonEntity,
    icemac.addressbook.interfaces.IMayHaveCustomizedPredfinedFields,
)
class File(BaseFile):
    """A file."""


file_entity = icemac.addressbook.entities.create_entity(
    _(u'file'), icemac.addressbook.file.interfaces.IFile, File)


@zope.component.adapter(icemac.addressbook.file.interfaces.IFile)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def title(file):
    """Title of the file."""
    return file.name
