from icemac.addressbook.i18n import _
import grokcore.component as grok
import icemac.addressbook.browser.base
import icemac.addressbook.browser.errormessage
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.menus.menu
import icemac.addressbook.browser.search.result.handler.update.operators
import icemac.addressbook.browser.wizard
import persistent.mapping
import z3c.wizard.step
import zope.component
import zope.interface
import zope.lifecycleevent


class UpdateWizard(icemac.addressbook.browser.wizard.Wizard):

    title = _(u'Update Wizard')
    confirmationPageName = '@@multi-update-completed'

    def setUpSteps(self):
        return [
            z3c.wizard.step.addStep(self, 'chooseField', weight=1),
            z3c.wizard.step.addStep(self, 'enterValue', weight=2),
            z3c.wizard.step.addStep(self, 'checkResult', weight=3),
        ]


class UpdateWizardBreadcrumb(
        icemac.addressbook.browser.breadcrumb.ModelBreadcrumb):
    """Breadcrumb for the UpdateWizard."""

    grok.adapts(
        UpdateWizard,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    @property
    def parent(self):
        return zope.component.getMultiAdapter(
            (icemac.addressbook.interfaces.IAddressBook(self.context),
             self.request), name='search.html')


UPDATE_SESSION_KEY = 'search_result_handler:update'


def get_update_data_session(request):
    """Get the session data for the current update."""
    session = icemac.addressbook.browser.base.get_session(request)
    data = session.get(UPDATE_SESSION_KEY, None)
    if data is None:
        data = persistent.mapping.PersistentMapping()
        session[UPDATE_SESSION_KEY] = data
    return data


def clean_update_data_session(request):
    """Clean the session data from the current update."""
    session = icemac.addressbook.browser.base.get_session(request)
    if session.get(UPDATE_SESSION_KEY, None) is not None:
        del session[UPDATE_SESSION_KEY]


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class SessionStorageStep(icemac.addressbook.browser.wizard.Step):
    """Step which stores its data in a dict in the session."""

    def getContent(self):
        return get_update_data_session(self.request)


def update_persons(persons, entity, field, operator_name, update_value):
    """Update `entity.field` of persons by using function and update_value.

    Return (errors, old_values) where each is a mapping between person ID and
    a value.
    """
    errors = dict()
    old_values = dict()
    for person in persons:
        schema_field = icemac.addressbook.entities.get_bound_schema_field(
            person, entity, field)
        current_value = schema_field.get(schema_field.context)
        old_values[person.__name__] = current_value
        operator = zope.component.getAdapter(
            current_value,
            icemac.addressbook.browser.search.result.handler.update.operators.
            IOperator, name=operator_name)
        try:
            new_value = operator(update_value)
        except Exception as e:
            errors[person.__name__] = (
                icemac.addressbook.browser.errormessage.render_error(
                    entity, schema_field.__name__, e))
        else:
            try:
                schema_field.set(schema_field.context, new_value)
            except zope.interface.Invalid as e:
                errors[person.__name__] = (
                    icemac.addressbook.browser.errormessage.render_error(
                        entity, schema_field.__name__, e))
            else:
                zope.lifecycleevent.modified(person)
    return errors, old_values


def get_fieldname_in_session(fieldname):
    """Return the name of the field used in the session."""
    return 'new_value.%s' % fieldname


update_views = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    'multi-update', 'chooseField', 'enterValue', 'checkResult')
