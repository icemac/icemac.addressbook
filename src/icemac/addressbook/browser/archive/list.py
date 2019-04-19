from icemac.addressbook.i18n import _
import icemac.addressbook.browser.breadcrumb
import icemac.addressbook.browser.person.list


class ArchiveList(icemac.addressbook.browser.person.list.PersonList):
    """List persons in the archive."""

    title = icemac.addressbook.browser.breadcrumb.DO_NOT_SHOW
    listing_title = _('Archived persons')
    no_rows_message = _(
        'There are no persons in the archive yet.'
        ' You can archive persons via the person edit view'
        ' or as a search result action.')
