import icemac.addressbook.browser.interfaces
import z3c.flashmessage.receiver
import zope.component
import zope.contentprovider.provider
import zope.interface


@zope.component.adapter(
    zope.interface.Interface,
    icemac.addressbook.browser.interfaces.IAddressBookLayer,
    zope.interface.Interface)
class MessagesContentProvider(
        zope.contentprovider.provider.ContentProviderBase,
        z3c.flashmessage.receiver.GlobalMessageReceiver):
    """Content provider displaying flash messages."""

    template = zope.browserpage.viewpagetemplatefile.ViewPageTemplateFile(
        'messages.pt')

    def update(self):
        self.messages = list(self.receive())

    def render(self):
        if self.messages:
            return self.template(self)
        return ''
