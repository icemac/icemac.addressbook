from icemac.addressbook.i18n import _
import grokcore.component as grok
import icemac.addressbook.browser.breadcrumb
import icemac.addressbook.interfaces


class ArchiveBreadCrumb(icemac.addressbook.browser.breadcrumb.Breadcrumb):
    """Breadcrumb for the archive."""

    grok.adapts(
        icemac.addressbook.interfaces.IArchive,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _('Archive')
