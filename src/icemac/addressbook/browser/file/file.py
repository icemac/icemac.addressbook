# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.base
import icemac.addressbook.file.file
import icemac.addressbook.file.interfaces
import os.path
import z3c.form.field
import z3c.form.widget
import zope.component
import zope.mimetype.interfaces
import zope.security.proxy


def cleanup_filename(filename):
    if filename is None:
        return _('<no name>')
    return filename.split('\\')[-1].split('/')[-1]


def update_blob(widget, file):
    """Update the mime type of the file.

    widget ... file upload widget
    file ... IFile instance to set the mime type on

    """
    if not widget.value:
        # no file uploaded
        return

    file.name = cleanup_filename(widget.filename)

    # At first we should try to replace the blob file with the one
    # uploaded, as this does not require reading and copying the file.
    # Zope stores the path to the file in the FileUpload in the `name`
    # attribute, but in tests it is stored in `filename` attribute, so
    # we have to differentiate.
    widget_file = widget.value
    file_name = getattr(widget_file, 'name', widget_file.filename)

    if os.path.exists(file_name):
        # If the file exists, use it.
        file.replace(file_name)
    else:
        # If not (python stores small files in a StringIO instead of a
        # real file on hard disk) update the contents.
        widget_file.seek(0)
        file.data = widget_file.read()

    try:
        widget_file.close()
    except OSError:
        # When the file was consumed (see file.replace) unlinking of the
        # original file fails as the path is wrong then.
        pass

    # get a sample of the file contents for fingerprinting
    fd = zope.security.proxy.removeSecurityProxy(file.open())
    data = fd.read(100)
    fd.close()

    content_type = widget.headers.get('Content-Type')
    if content_type == 'application/octet-stream':
        content_type = None
    mime_type_getter = zope.component.getUtility(
        zope.mimetype.interfaces.IMimeTypeGetter)
    mime_type = mime_type_getter(data=data, content_type=content_type,
                                 name=cleanup_filename(widget.filename))
    if not mime_type:
        mime_type = 'application/octet-stream'
    file.mimeType = mime_type


class Add(icemac.addressbook.browser.base.BaseAddForm):
    "Add a file."

    label = _(u'Add file')
    class_ = icemac.addressbook.file.file.File
    interface = icemac.addressbook.file.interfaces.IFile
    next_url = 'parent'

    @property
    def fields(self):
        return z3c.form.field.Fields(
            *icemac.addressbook.interfaces.IEntity(
                self.interface).getFieldValuesInOrder()).omit(
            'name', 'mimeType', 'size')

    def create(self, data):
        file = super(Add, self).create(data)
        update_blob(self.widgets['data'], file)
        if hasattr(self.context, 'file_marker_interface'):
            zope.interface.directlyProvides(
                file, zope.security.proxy.removeSecurityProxy(
                    self.context.file_marker_interface))
        return file


# in the Add form file upload is required ...
IFile_data_required = z3c.form.widget.StaticWidgetAttribute(
    True, context=None, request=None, view=Add,
    field=icemac.addressbook.file.interfaces.IFile['data'], widget=None)

# ... but not in all other forms
IFile_data_not_required = z3c.form.widget.StaticWidgetAttribute(
    False, context=icemac.addressbook.file.interfaces.IFile,
    request=None, view=None,
    field=icemac.addressbook.file.interfaces.IFile['data'], widget=None)


class Edit(icemac.addressbook.browser.base.BaseEditFormWithCancel):
    "Edit a file."

    interface = icemac.addressbook.file.interfaces.IFile
    next_url = 'parent'

    def applyChanges(self, data):
        super(Edit, self).applyChanges(data)
        update_blob(self.widgets['data'], self.context)


class DeleteFileForm(icemac.addressbook.browser.base.BaseDeleteForm):
    "Are you sure question for deleting a file."

    next_url = 'parent'
    label = _(u'Do you really want to delete this file?')
    interface = icemac.addressbook.file.interfaces.IFile
    field_names = ('name', )
