from icemac.addressbook.i18n import _
import icemac.addressbook.interfaces
import zc.sourcefactory.basic
import zope.component


def tokenize(entity, field_name):
    """Convert an entity and a field_name into a unique string token."""
    return "%s###%s" % (entity.name, field_name)


def untokenize(token):
    """Convert a token containing entity and field name back to the objects."""
    entity_name, field_name = token.split('###')
    entity = icemac.addressbook.interfaces.IEntity(entity_name)
    field = entity.getRawField(field_name)
    return entity, field


class Source(zc.sourcefactory.basic.BasicSourceFactory):
    """Fields of a person."""

    def getValues(self):
        # Only the main entities (the ones with default values on the
        # person) are in this source as only their presence is guaranteed.
        entities = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities)
        for entity in entities.getMainEntities():
            # All fields, even the user defined ones, can show up here.
            for field_name, field in entity.getRawFields():
                # We return a representation here which can be stored in
                # ZODB even though it is not so easy to compute a title from
                # it. But it would be more difficult to adapt consumers of
                # this source (e. g. zope.preference) to store a string
                # instead of non-persistent field objects.
                yield tokenize(entity, field_name)

    def getTitle(self, value):
        entity, field = untokenize(value)
        field_title = icemac.addressbook.entities.get_field_label(field)
        # The titles might be message ids so allow to translate them.
        return _(u"${prefix} -- ${title}", mapping=dict(
            prefix=entity.title, title=field_title))


source = Source()
