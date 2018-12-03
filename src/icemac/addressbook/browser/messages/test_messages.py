from .messages import UserSpecificRAMMessageSource
import zope.publisher.testing


def test_messages__UserSpecificRAMMessageSource___get_storage__1(address_book):
    """It returns the messages only for the current user."""
    source = UserSpecificRAMMessageSource()
    with zope.publisher.testing.interaction('principal_1'):
        source.send(u'msg 1')
        source.send(u'msg 2')

    with zope.publisher.testing.interaction('principal_2'):
        # no messages of other users
        assert [] == list(source.list())
        source.send(u'my msg')
        source.send(u'my msg, too')
        # but own messages
        assert ([u'my msg', u'my msg, too']
                == [x.message for x in source.list()])
