# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
import zope.interface
import zope.schema
import zope.mimetype.interfaces


class IFile(zope.interface.Interface):
    """A file uploaded from harddisk to addressbook."""

    name = zope.schema.TextLine(
        title=_(u'file name'), description=_(u'Name of the file.'))

    mimeType = zope.mimetype.interfaces.IContentTypeAware['mimeType']

    data = zope.schema.Bytes(title=_('file'))

    size = zope.schema.Int(
        title=_("Size"), description=_("Size in bytes"),
        readonly=True, required=True)

    def open(mode="r"):
        """Return an object providing access to the file data.

        Allowed values for `mode` are 'r' (read); 'w' (write); 'a' (append) and
        'r+' (read/write).  Other values cause `ValueError` to be raised.

        If the file is opened in read mode, an object with an API (but
        not necessarily interface) of `IFileReader` is returned; if
        opened in write mode, an object with an API of `IFileWriter` is
        returned; if in read/write, an object that implements both is
        returned.

        All readers and writers operate in 'binary' mode.

        """

    def openDetached():
        """Return file data disconnected from database connection.

        Read access only.
        """

    def replace(filename):
        """Replace with another file.

        CAUTION: The file given as argument gets consumed!
        """


class IFileContainer(zope.interface.Interface):
    """Marker interface for container which can contain files."""
