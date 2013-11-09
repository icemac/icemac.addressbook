# -*- coding: latin-1 -*-
# Copyright (c) 2008-2013 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
import gocept.reference.interfaces
import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.metadata
import icemac.addressbook.interfaces
import icemac.addressbook.person
import icemac.addressbook.utils
import transaction
import z3c.form.button
import z3c.form.datamanager
import z3c.form.form
import z3c.form.group
import zc.sourcefactory.contextual
import zope.interface


class AddGroup(icemac.addressbook.browser.base.PrefixGroup):
    "PrefixGroup for AddForm."

    def __init__(self, context, request, parent, interface, label, prefix):
        super(AddGroup, self).__init__(context, request, parent)
        self.interface = interface
        self.label = label
        self.prefix = prefix


class PersonEditGroup(AddGroup):
    """PrefixGroup for addresses IPerson in EditForm."""

    def __init__(self, context, request, parent, interface, label, prefix,
                 index, key):
        super(PersonEditGroup, self).__init__(
            context, request, parent, interface, label, prefix)
        self.prefix = "%s_%s" % (prefix, index)
        self.key = key

    def update(self):
        self.groups = [
            icemac.addressbook.browser.metadata.MetadataGroup(
                self.getContent(), self.request, self)]
        super(PersonEditGroup, self).update()


class AddressEditGroup(PersonEditGroup):
    "PrefixGroup for addresses in EditForm."

    def getContent(self):
        return self.context[self.key]


class FileEditGroup(AddressEditGroup):
    "AddressEditGroup for icemac.addressbook.file.interfaces.IFile objects."


class DefaultSelectGroup(icemac.addressbook.browser.base.PrefixGroup):
    """Group to select the default addresses."""

    interface = icemac.addressbook.interfaces.IPersonDefaults
    label = icemac.addressbook.person.person_defaults_entity.title
    prefix = 'defaults'


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class PersonAddForm(z3c.form.group.GroupForm,
                    icemac.addressbook.browser.base.BaseAddForm):
    """Add a person."""
    label = _(u'Add new person')
    next_url = 'parent'
    next_view = 'person-list.html'
    interface_for_menu = icemac.addressbook.interfaces.IPerson

    def __init__(self, *args, **kw):
        super(PersonAddForm, self).__init__(*args, **kw)
        context = self.context
        request = self.request
        entities = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities)
        groups = [AddGroup(context, request, self, entity.interface,
                           entity.title, entity.name)
                  for entity in entities.getMainEntities()]
        self.groups = tuple(groups)

    def createAndAdd(self, data):
        # Create person first
        person_entity = icemac.addressbook.interfaces.IEntity(
            icemac.addressbook.interfaces.IPerson)
        person_entity_name = person_entity.name
        for group in self.groups:
            if group.prefix == person_entity_name:
                # found person group, now can create person object
                person = icemac.addressbook.browser.base.create(
                    group, person_entity.getClass(), data)
                break
        self._name = icemac.addressbook.utils.add(self.context, person)
        for group in self.groups:
            if group.prefix == person_entity_name:
                # already created above
                continue
            entity = icemac.addressbook.interfaces.IEntity(group.prefix)
            obj = icemac.addressbook.browser.base.create(
                group, entity.getClass(), data)
            icemac.addressbook.utils.add(person, obj)
            # handling of default addresses: the first address is
            # saved as default
            default_attrib = entity.tagged_values['default_attrib']
            if getattr(person, default_attrib, None) is None:
                setattr(person, default_attrib, obj)
        self.obj = person
        return person


def person_deletable(form):
    "Button display constraint which checks whether a person is deleteable."
    person = form.context
    ref_target = gocept.reference.interfaces.IReferenceTarget(person)
    return not ref_target.is_referenced(recursive=False)


class PersonEditForm(icemac.addressbook.browser.base.GroupEditForm):

    label = _(u'Edit person data')
    next_url = 'parent'
    next_view = 'person-list.html'
    interface_for_menu = icemac.addressbook.interfaces.IPerson

    def __init__(self, *args, **kw):
        super(PersonEditForm, self).__init__(*args, **kw)
        entity_util = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities)
        entities = entity_util.getMainEntities(sorted=False)
        file_entity = icemac.addressbook.interfaces.IEntity(
            icemac.addressbook.file.interfaces.IFile)
        defaults_entity = icemac.addressbook.interfaces.IEntity(
            icemac.addressbook.interfaces.IPersonDefaults)
        entities.extend([file_entity, defaults_entity])

        groups = []
        for entity in icemac.addressbook.entities.sorted_entities(entities):
            index = 0

            # Special handling for IPerson
            if entity.interface == icemac.addressbook.interfaces.IPerson:
                group = PersonEditGroup(
                    self.context, self.request, self, entity.interface,
                    entity.title, entity.name, index,
                    self.context.__name__)
                groups.append(group)
                continue

            # Special handling for IPersonDefaults
            IPersonDefaults = icemac.addressbook.interfaces.IPersonDefaults
            if entity.interface == IPersonDefaults:
                groups.append(
                    DefaultSelectGroup(self.context, self.request, self))
                continue

            is_ifile = (
                entity.interface == icemac.addressbook.file.interfaces.IFile)
            if is_ifile:
                # IFile needs a special group and has a fix title
                group_class = FileEditGroup
                obj_title = entity.title
            else:
                # for the other entities the title depends on whether being
                # main address or not
                default_attrib = entity.tagged_values.get('default_attrib')
                default_obj = getattr(self.context, default_attrib)
                group_class = AddressEditGroup

            for obj in icemac.addressbook.utils.iter_by_interface(
                    self.context, entity.interface):
                if not is_ifile:
                    if obj == default_obj:
                        obj_title = _(u'main ${address}')
                    else:
                        obj_title = _(u'other ${address}')
                    obj_title = _(obj_title, mapping={'address': entity.title})
                group = group_class(
                    self.context, self.request, self, entity.interface,
                    obj_title, entity.name, index, obj.__name__)
                groups.append(group)
                index += 1

        self.groups = tuple(groups)

    @z3c.form.button.buttonAndHandler(_('Apply'), name='apply')
    def handleApply(self, action):
        super(PersonEditForm, self).handleApply(self, action)
        # update file's mime type after new file was uploaded
        for group in self.groups:
            if not isinstance(group, FileEditGroup):
                continue
            prefix = z3c.form.util.expandPrefix(group.prefix)
            icemac.addressbook.browser.file.file.update_blob(
                group.widgets[prefix + 'data'], group.getContent())

    @z3c.form.button.buttonAndHandler(
        _(u'Clone person'), name='clone_person',
        condition=icemac.addressbook.browser.base.can_access('@@clone.html'))
    def handleClonePerson(self, action):
        self.redirect_to_next_url('object', '@@clone.html')

    @z3c.form.button.buttonAndHandler(
        _(u'Delete whole person'), name='delete_person',
        condition=icemac.addressbook.browser.base.all_(
            icemac.addressbook.browser.base.can_access('@@delete_person.html'),
            person_deletable))
    def handleDeletePerson(self, action):
        self.redirect_to_next_url('object', '@@delete_person.html')

    @z3c.form.button.buttonAndHandler(
        _(u'Delete single entry'), name='delete_entry',
        condition=icemac.addressbook.browser.base.can_access(
            '@@delete_entry.html'))
    def handleDeleteAddress(self, action):
        self.redirect_to_next_url('object', '@@delete_entry.html')

    def applyChanges(self, data):
        """Special variant which sends ModifiedEvent for each modified
        object. (not to be used universally!)"""
        content = self.getContent()
        changed = {}
        mainChanged = z3c.form.form.applyChanges(self, content, data)
        if mainChanged:
            changed[content] = mainChanged
        for group in self.groups:
            groupChanged = group.applyChanges(data)
            if groupChanged:
                changed[group.getContent()] = groupChanged
        for content, changes in changed.items():
            descriptions = [
                zope.lifecycleevent.Attributes(interface, *names)
                for interface, names in changes.items()]
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(
                    content, *descriptions))
        return changed


class KeywordDataManager(z3c.form.datamanager.AttributeField):
    """Datamanager which converts the internal InstrumentedSet into a
    set to be compareable with selected values."""

    def get(self):
        return set(x for x in super(KeywordDataManager, self).get())


class DeletePersonForm(icemac.addressbook.browser.base.BaseDeleteForm):
    label = _(u'Do you really want to delete this person?')
    interface = icemac.addressbook.interfaces.IPerson
    field_names = ('first_name', 'last_name')
    next_view_after_delete = 'person-list.html'

    def _do_delete(self):
        try:
            super(DeletePersonForm, self)._do_delete()
        except gocept.reference.interfaces.IntegrityError:
            transaction.abort()
            message = _(
                'Failed to delete person: This person is referenced. '
                'To delete this person, remove the reference before.')
            zope.component.getUtility(
                z3c.flashmessage.interfaces.IMessageSource).send(message)


class ClonePersonForm(icemac.addressbook.browser.base.BaseCloneForm):
    label = _(u'Do you really want to clone this person?')
    interface = icemac.addressbook.interfaces.IPerson
    field_names = ('first_name', 'last_name')


class PersonEntriesSource(
    zc.sourcefactory.contextual.BasicContextualSourceFactory):
    "Source to select entries (addresses, files, ...) from a person."

    def getValues(self, context):
        entities = zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities).getEntities()
        for entity in entities:
            if entity.interface is None:
                continue
            source = icemac.addressbook.interfaces.ContextByInterfaceSource(
                entity.interface).factory.getValues(context)
            for value in source:
                yield value

    def getTitle(self, context, value):
        entity = icemac.addressbook.interfaces.IEntity(value)
        title = _('${prefix} -- ${title}',
                  mapping=dict(
                      prefix=entity.title,
                      title=icemac.addressbook.interfaces.ITitle(value)))
        return title


class IPersonEntries(zope.interface.Interface):
    """Content entries of a person."""

    entry = zope.schema.Choice(
        title=_(u'Entries'), source=PersonEntriesSource())


class DeleteSingleEntryForm(icemac.addressbook.browser.base.BaseEditForm):
    """Form to choose entry for deletion."""

    label = _(u'Please choose an entry for deletion:')
    interface = IPersonEntries
    ignoreContext = True
    next_url = 'object'

    @z3c.form.button.buttonAndHandler(_(u'Delete entry'), name='delete_entry')
    def handleDeleteEntry(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        selected_entry = data['entry']

        url = self.url(selected_entry)
        self.request.response.redirect(url + '/@@delete.html')
