from icemac.addressbook.i18n import _
import icemac.addressbook.interfaces
import zope.schema.fieldproperty
import icemac.addressbook.utils
import persistent
import zope.catalog.interfaces
import zope.component
import zope.container.btree
import zope.container.contained
import zope.interface
import zope.lifecycleevent


@zope.interface.implementer(icemac.addressbook.interfaces.IKeywords)
class KeywordContainer(zope.container.btree.BTreeContainer):
    """A container for keywords."""

    def get_keywords(self):
        # sorting will be done in presentation layer
        return self.values()

    def get_keyword_by_title(self, title, default=None):
        for keyword in self.values():
            if keyword.title == title:
                return keyword
        return default


@zope.interface.implementer(icemac.addressbook.interfaces.IKeyword)
class Keyword(persistent.Persistent, zope.container.contained.Contained):
    """A keyword."""

    zope.schema.fieldproperty.createFieldProperties(
        icemac.addressbook.interfaces.IKeyword)

    def __init__(self, title=None):
        super(Keyword, self).__init__()
        if title is not None:
            self.title = title


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
