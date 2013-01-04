# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
import icemac.addressbook.interfaces
import icemac.addressbook.utils
import persistent
import zope.catalog.interfaces
import zope.component
import zope.container.btree
import zope.container.contained
import zope.interface
import zope.lifecycleevent
import zope.schema.fieldproperty


class KeywordContainer(zope.container.btree.BTreeContainer):
    "A container for keywords."
    zope.interface.implements(icemac.addressbook.interfaces.IKeywords)

    def get_keywords(self):
        # sorting will be done in presentation layer
        return self.values()

    def get_keyword_by_title(self, title, default=None):
        for keyword in self.values():
            if keyword.title == title:
                return keyword
        return default


class Keyword(persistent.Persistent, zope.container.contained.Contained):
    "A keyword."
    zope.interface.implements(icemac.addressbook.interfaces.IKeyword)

    def __init__(self, title=None):
        super(Keyword, self).__init__()
        if title is not None:
            self.title = title

    title = zope.schema.fieldproperty.FieldProperty(
        icemac.addressbook.interfaces.IKeyword['title'])


keyword_entity = icemac.addressbook.entities.create_entity(
    _(u'keyword'), icemac.addressbook.interfaces.IKeyword, Keyword)


@zope.component.adapter(icemac.addressbook.interfaces.IKeyword,
                        zope.lifecycleevent.IObjectModifiedEvent)
def changed(obj, event):
    for desc in event.descriptions:
        if (desc.interface == icemac.addressbook.interfaces.IKeyword and
            'title' in desc.attributes):
            catalog = zope.component.getUtility(
                zope.catalog.interfaces.ICatalog)
            catalog.updateIndex(catalog.get('keywords'))
            break


uniqueTitles = icemac.addressbook.utils.unique_by_attr_factory(
    'title', _(u'This keyword already exists.'))
