# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.personlist
import icemac.addressbook.browser.table
import zope.interface


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class PersonList(
        icemac.addressbook.browser.personlist.BasePersonList,
        icemac.addressbook.browser.table.PageletTable):
    """List persons in address book."""

    title = _('Person list')
    listing_title = _('Persons')
    no_rows_message = _(
        u'There are no persons entered yet, click on "Add person" to create '
        u'one.')

    def __init__(self, *args, **kw):
        super(PersonList, self).__init__(*args, **kw)
        self.batchSize = self.prefs.personListTab.batch_size
        self.startBatchingAt = self.batchSize

    @property
    def values(self):
        """The values are stored on the context."""
        return self.context.values()
