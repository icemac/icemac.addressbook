from icemac.addressbook.i18n import _
import grokcore.component as grok
import icemac.addressbook.browser.base
import icemac.addressbook.browser.breadcrumb
import icemac.addressbook.browser.interfaces


class MasterData(object):
    """List of master data."""


class MasterDataBreadCrumb(
        icemac.addressbook.browser.breadcrumb.Breadcrumb):
    """Breadcrumb for the master data view."""

    grok.adapts(
        MasterData,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _('Master data')
