import icemac.addressbook.browser.interfaces
import z3c.flashmessage.receiver
import zope.component
import zope.contentprovider.provider
import zope.interface


class MessagesContentProvider(
        zope.contentprovider.provider.ContentProviderBase,
        z3c.flashmessage.receiver.GlobalMessageReceiver):
    """Content provider displaying flash messages."""

    zope.component.adapts(
        zope.interface.Interface,
        icemac.addressbook.browser.interfaces.IAddressBookLayer,
        zope.interface.Interface)

    template = zope.browserpage.viewpagetemplatefile.ViewPageTemplateFile(
        'messages.pt')

    def update(self):
        self.messages = list(self.receive())

    def render(self):
        if self.messages:
            return self.template(self)
        return ''
