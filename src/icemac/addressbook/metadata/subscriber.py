import icemac.addressbook.metadata.interfaces
import six
import zope.component
import zope.lifecycleevent
import zope.security.management
import zope.security.proxy


def set_current_princial_id(object, attribute):
    """Get the id of the current principal."""
    interaction = zope.security.management.queryInteraction()
    if interaction is None:
        return
    # Seting the first participating principal is enough for now.
    participation = interaction.participations[0]
    # Need to unwrap the object otherwise we get:
    # ForbiddenAttribute: ('__getitem__',
    #                      <BTrees.OOBTree.OOBTree object...>)
    # when trying to access the annotation key.
    unsafe_object = zope.security.proxy.getObject(object)
    metadata = icemac.addressbook.metadata.interfaces.IEditor(unsafe_object)
    setattr(metadata, attribute, six.text_type(participation.principal.title))


@zope.component.adapter(
    zope.annotation.interfaces.IAttributeAnnotatable,
    zope.lifecycleevent.IObjectCreatedEvent)
def CreatorAnnotator(object, event):
    """Set creator on object."""
    set_current_princial_id(object, 'creator')


def LastModifierAnnotator(object, event):
    """Set last modifier on object."""
    set_current_princial_id(object, 'modifier')
