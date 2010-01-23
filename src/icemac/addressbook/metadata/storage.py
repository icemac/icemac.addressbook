# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

import icemac.addressbook.metadata.interfaces
import persistent
import zope.component
import zope.interface


class EditorMetadataStorage(persistent.Persistent):
    """Storage for editor metadata in annotations."""

    zope.component.adapts(zope.interface.Interface)
    zope.interface.implements(icemac.addressbook.metadata.interfaces.IEditor)

    creator = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.metadata.interfaces.IEditor['creator'])
    modifier = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.metadata.interfaces.IEditor['modifier'])


editor_metadata_storage = zope.annotation.factory(
    EditorMetadataStorage, key='icemac.metadata')
