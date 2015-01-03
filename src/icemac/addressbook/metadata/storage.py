# Copyright (c) 2010-2014 Michael Howitz
# See also LICENSE.txt
import icemac.addressbook.metadata.interfaces
import zope.schema.fieldproperty
import persistent
import zope.component
import zope.interface


class EditorMetadataStorage(persistent.Persistent):
    """Storage for editor metadata in annotations."""

    zope.component.adapts(zope.interface.Interface)
    zope.interface.implements(icemac.addressbook.metadata.interfaces.IEditor)
    zope.schema.fieldproperty.createFieldProperties(
        icemac.addressbook.metadata.interfaces.IEditor)


editor_metadata_storage = zope.annotation.factory(
    EditorMetadataStorage, key='icemac.metadata')
