import icemac.addressbook.generations.utils
import icemac.addressbook.interfaces
import zope.component


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(ab):
    """Update user generated fields.

    They get the information about the entity interface they belong to.

    """
    entities = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntities)
    for entity in entities.getEntities(sorted=False):
        for name, field in entity.getRawFields(sorted=False):
            if icemac.addressbook.interfaces.IField.providedBy(field):
                field.interface = entity.interface
