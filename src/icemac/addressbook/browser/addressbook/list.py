# -*- coding: utf-8 -*-
# Copyright (c) 2009-2011 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import _
import icemac.addressbook.browser.personlist
import icemac.addressbook.browser.table


class PersonList(
    icemac.addressbook.browser.personlist.BasePersonList,
    icemac.addressbook.browser.table.PageletTable):
    """List persons in address book."""

    no_rows_message = _(
        u'There are no persons entered yet, click on "Add person" to create '
        u'one.')

    def __init__(self, *args, **kw):
        super(PersonList, self).__init__(*args, **kw)
        self.startBatchingAt = self.prefs.batch_size
        self.batchSize = self.prefs.batch_size

    @property
    def values(self):
        """The values are stored on the context."""
        return self.context.values()
