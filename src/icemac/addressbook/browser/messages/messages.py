# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

from hurry.jquery import jquery
import icemac.addressbook.browser.interfaces
import z3c.flashmessage.receiver
import zope.component
import zope.contentprovider.interfaces
import zope.contentprovider.provider
import zope.interface


class MessagesContentProvider(
    zope.contentprovider.provider.ContentProviderBase,
    z3c.flashmessage.receiver.GlobalMessageReceiver):
    """Content provider displaying flash messages."""

    zope.component.adapts(zope.interface.Interface,
                          icemac.addressbook.browser.interfaces.IAddressBookLayer,
                          zope.interface.Interface)

    template = zope.browserpage.viewpagetemplatefile.ViewPageTemplateFile(
        'messages.pt')

    def update(self):
        jquery.need()
        self.messages = list(self.receive())

    def render(self):
        return self.template(self)
