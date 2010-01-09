# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import ZODB.blob
import classproperty
import icemac.addressbook.entities
import icemac.addressbook.file.interfaces
import icemac.addressbook.interfaces
import persistent
import zope.container.contained
import zope.interface


class File(persistent.Persistent, zope.container.contained.Contained):
    "A file."

    zope.interface.implements(icemac.addressbook.file.interfaces.IFile)

    def __init__(self, *args, **kw):
        super(File, self).__init__(*args, **kw)
        # initialize blob with no data
        self._data = ZODB.blob.Blob()
        self.data = ''

    name = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.file.interfaces.IFile['name'])
    mimeType = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.file.interfaces.IFile['mimeType'])

    @property
    def size(self):
        reader = self.open()
        reader.seek(0,2)
        size = int(reader.tell())
        reader.close()
        return size

    class data(classproperty.classproperty):
        def __get__(self):
            # This method can't be used to read the data, use
            # openDetached instead. This is necessary because of the
            # stupidity of z3c.form which reads the whole file when
            # rendering a form.
            return ''
        def __set__(self, data):
            fp = self.open('w')
            fp.write(data)
            fp.close()

    def replace(self, filename):
        "Replace with anoher file."
        self._data.consumeFile(filename)

    def openDetached(self, mode='r'):
        return file(self._data.committed(), 'rb')

    def open(self, mode='r'):
        return self._data.open(mode)


file_entity = icemac.addressbook.entities.create_entity(
    _(u'file'), icemac.addressbook.file.interfaces.IFile, File)


@zope.component.adapter(icemac.addressbook.file.interfaces.IFile)
@zope.interface.implementer(icemac.addressbook.interfaces.ITitle)
def title(file):
    """Title of the file."""
    return file.name
