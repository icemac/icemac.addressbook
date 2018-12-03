import icemac.addressbook.browser.interfaces
import textwrap
import z3c.flashmessage.receiver
import z3c.flashmessage.sources
import zope.component
import zope.contentprovider.provider
import zope.interface
import zope.security.management
import zope.session.interfaces


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
    message_display_timeout = 3000  # ms

    def update(self):
        self.messages = list(self.receive())

    def render(self):
        if self.messages:
            return self.template(self)
        return ''

    def js(self):
        return textwrap.dedent('''
            $(document).ready(function() {
                setTimeout(
                    function() {
                        $("#info-messages").fadeOut("normal")
                    },
                    %d);
                })
        ''' % self.message_display_timeout)


class UserSpecificRAMMessageSource(
        z3c.flashmessage.sources.ListBasedMessageSource):
    """Flashmessage source which stores its data per user in RAM."""

    def __init__(self):
        self._user_storage = {}

    def _get_storage(self, for_write=False):
        request = zope.security.management.getInteraction().participations[0]
        client_id = str(zope.session.interfaces.IClientId(request))
        return self._user_storage.setdefault(client_id, [])
