from icemac.addressbook.i18n import _
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
import icemac.addressbook.browser.interfaces
import icemac.addressbook.file.interfaces
import z3c.form.browser.file
import z3c.form.converter
import z3c.form.interfaces
import z3c.form.widget
import zope.component
import zope.schema.interfaces


class FileWidget(z3c.form.browser.file.FileWidget):
    """FileWidget for use with ..file.interfaces.IFile['data']."""

    download_template = ViewPageTemplateFile('widget_download.pt')

    @property
    def href(self):
        view = zope.component.getMultiAdapter(
            (self.context, self.request), name='download.html')
        url = zope.component.getMultiAdapter(
            (view, self.request), name='absolute_url')
        return url

    content = _('Download file')

    @property
    def download(self):
        if icemac.addressbook.file.interfaces.IFile.providedBy(self.context):
            return self.download_template(self)
        return ''


@zope.component.adapter(
    zope.schema.interfaces.IBytes,
    icemac.addressbook.browser.interfaces.IAddressBookLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def FileFieldWidget(field, request):
    """Adapt IBytes to FileWidget."""
    return z3c.form.widget.FieldWidget(field, FileWidget(request))


class FileUploadDataConverter(z3c.form.converter.FileUploadDataConverter):
    """Coverter which does not read the whole file contents into a variable."""

    def toFieldValue(self, value):
        """Convert value to be stored.

        CAUTION: Does not return the file contents but only the first
        byte, to signal that a file was uploaded.

        """
        if value is None or value == '':
            # When no new file is uploaded, send a signal that we do not want
            # to do anything special.
            return z3c.form.interfaces.NOT_CHANGED

        # We expect here to have a FileUpload instance.  We store the
        # additional FileUpload values on the widget before we loose
        # them.
        self.widget.headers = value.headers
        self.widget.filename = value.filename
        value.seek(0)
        data = value.read(1)
        return data
