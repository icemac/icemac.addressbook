import icemac.addressbook.fieldsource
import icemac.addressbook.interfaces
import zope.app.appsetup.bootstrap
import zope.preference.default
import zope.preference.interfaces
import zope.component


def add(address_book):
    """Add a default preferences provider to the address book."""
    # Add a default preferences utility on the address book site.
    default_prefs = zope.app.appsetup.bootstrap.ensureUtility(
        address_book,
        zope.preference.interfaces.IDefaultPreferenceProvider, '',
        zope.preference.default.DefaultPreferenceProvider)
    if default_prefs is None:
        default_prefs = zope.component.getUtility(
            zope.preference.interfaces.IDefaultPreferenceProvider)

    # Set the defaults for the person lists.
    personLists = default_prefs.getDefaultPreferenceGroup('ab.personLists')
    personLists.columns = []
    # The default columns are person last name and person first name.
    person_entity = icemac.addressbook.interfaces.IEntity(
        icemac.addressbook.interfaces.IPerson)
    personLists.columns.append(
        icemac.addressbook.fieldsource.tokenize(person_entity, 'last_name'))
    personLists.columns.append(
        icemac.addressbook.fieldsource.tokenize(person_entity, 'first_name'))
    personLists._p_changed = True
    # The default sort column is person last name.
    personLists.order_by = icemac.addressbook.fieldsource.tokenize(
        person_entity, 'last_name')
    # The default sort direction is ascending
    personLists.sort_direction = 'ascending'

    # Set the defaults for the person list tab:
    prefs = default_prefs.getDefaultPreferenceGroup('ab.personListTab')
    prefs.batch_size = 20

    # Set the default time zone:
    prefs = default_prefs.getDefaultPreferenceGroup('ab.timeZone')
    prefs.time_zone = 'UTC'
