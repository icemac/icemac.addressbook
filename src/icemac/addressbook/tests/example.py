import zope.component
import z3c.flashmessage.interfaces


class PageTestGetMessages(object):
    """Test page to send messages using z3c.flashmessage."""

    def __call__(self, msg):
        zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageSource).send(msg)
        return 'Message %r sent.' % msg
