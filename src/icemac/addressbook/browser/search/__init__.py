# Copyright (c) 2008-2014 Michael Howitz
# See also LICENSE.txt
import icemac.addressbook.browser.interfaces
import zope.interface


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class Search(object):
    """View to select a search."""
    show_headline = True
    form_explanation = u''
