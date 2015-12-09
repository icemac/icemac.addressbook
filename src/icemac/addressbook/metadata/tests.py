
import unittest


class TestMetadata(unittest.TestCase):

    def test_implements(self):
        import zope.interface.verify
        import icemac.addressbook.metadata.interfaces
        import icemac.addressbook.metadata.storage
        self.assert_(zope.interface.verify.verifyObject(
            icemac.addressbook.metadata.interfaces.IEditor,
            icemac.addressbook.metadata.storage.EditorMetadataStorage()))
