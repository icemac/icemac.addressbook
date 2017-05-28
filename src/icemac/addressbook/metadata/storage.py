import icemac.addressbook.metadata.interfaces
import zope.schema.fieldproperty
import persistent
import zope.component
import zope.interface


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(icemac.addressbook.metadata.interfaces.IEditor)
class EditorMetadataStorage(persistent.Persistent):
    """Storage for editor metadata in annotations."""

    zope.schema.fieldproperty.createFieldProperties(
        icemac.addressbook.metadata.interfaces.IEditor)


editor_metadata_storage = zope.annotation.factory(
    EditorMetadataStorage, key='icemac.metadata')
