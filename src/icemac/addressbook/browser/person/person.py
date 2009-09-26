# -*- coding: latin-1 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$

from icemac.addressbook.i18n import MessageFactory as _
import gocept.reference.interfaces
import icemac.addressbook.address
import icemac.addressbook.browser.base
import icemac.addressbook.browser.metadata
import icemac.addressbook.interfaces
import icemac.addressbook.person
import icemac.addressbook.sources
import icemac.addressbook.utils
import z3c.form.button
import z3c.form.datamanager
import z3c.form.field
import z3c.form.group
import z3c.form.interfaces
import zc.sourcefactory.contextual
import zope.component
import zope.traversing.browser.interfaces


class AddGroup(icemac.addressbook.browser.base.PrefixGroup):
    "PrefixGroup for AddForm."

    def __init__(self, context, request, parent, interface, label, prefix):
        super(AddGroup, self).__init__(context, request, parent)
        self.interface = interface
        self.label = label
        self.prefix = prefix


class EditGroup(AddGroup):
    "PrefixGroup for EditForm."

    groups = (icemac.addressbook.browser.metadata.ModifiedGroup,)

    def __init__(
        self, context, request, parent, interface, label, prefix, index, key):
        super(EditGroup, self).__init__(
            context, request, parent, interface, label, prefix)
        self.prefix = "%s_%s" % (prefix, index)
        self.key = key

    def getContent(self):
        return self.context[self.key]


class FileEditGroup(EditGroup):
    """EditGroup for icemac.addressbook.file.interfaces.IFile objects."""

    @property
    def fields(self):
        return super(FileEditGroup, self).fields


class DefaultSelectGroup(icemac.addressbook.browser.base.PrefixGroup):
    """Group to select the default addresses."""

    interface = icemac.addressbook.interfaces.IPersonDefaults
    label = _(u'main adresses and numbers')
    prefix = 'defaults'


class PersonAddForm(z3c.form.group.GroupForm,
                    icemac.addressbook.browser.base.BaseAddForm):

    label = _(u'Add new person')
    interface = icemac.addressbook.interfaces.IPerson
    next_url = 'parent'

    def __init__(self, *args, **kw):
        super(PersonAddForm, self).__init__(*args, **kw)
        context = self.context
        request = self.request
        groups = [AddGroup(context, request, self, address['interface'],
                           _(address['title']), address['prefix'])
                  for address in icemac.addressbook.address.address_mapping]
        self.groups = tuple(groups)

    def createAndAdd(self, data):
        person = icemac.addressbook.browser.base.create(
            self, icemac.addressbook.person.Person, data)
        self._name = icemac.addressbook.utils.add(self.context, person)
        for group in self.groups:
            obj = icemac.addressbook.browser.base.create(
                group, icemac.addressbook.address.prefix_to_class(group.prefix),
                data)
            icemac.addressbook.utils.add(person, obj)
            # handling of default addresses: the first address is
            # saved as default
            default_attrib = 'default_%s' % group.prefix
            if getattr(person, default_attrib, None) is None:
                setattr(person, default_attrib, obj)
        return person


def person_deletable(form):
    "Button display constraint which checks whether a person is deleteable."
    person = form.context
    ref_target = gocept.reference.interfaces.IReferenceTarget(person)
    return not ref_target.is_referenced(recursive=False)


class PersonEditForm(
    z3c.form.group.GroupForm, icemac.addressbook.browser.base.BaseEditForm):

    label = _(u'Edit person data')
    interface = icemac.addressbook.interfaces.IPerson
    next_url = 'parent'

    def __init__(self, *args, **kw):
        super(PersonEditForm, self).__init__(*args, **kw)
        groups = [icemac.addressbook.browser.metadata.ModifiedGroup,
                  DefaultSelectGroup]
        for address in icemac.addressbook.address.address_mapping:
            index = 0
            default_obj = getattr(self.context,
                                  'default_%s' % address['prefix'])
            for obj in icemac.addressbook.utils.iter_by_interface(
                    self.context, address['interface']):
                if obj == default_obj:
                    obj_title = u'main ' + address['title']
                else:
                    obj_title = u'other ' + address['title']
                group = EditGroup(
                    self.context, self.request, self, address['interface'],
                    _(obj_title), address['prefix'], index, obj.__name__)
                groups.append(group)
                index += 1

        iface = icemac.addressbook.file.interfaces.IFile
        for obj in icemac.addressbook.utils.iter_by_interface(
                self.context, iface):
            group = FileEditGroup(
                self.context, self.request, self, iface, _(u'file'), 'file',
                index, obj.__name__)
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
                group.widgets[prefix+'data'], group.getContent())

    @z3c.form.button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        self.status = self.noChangesMessage

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


class KeywordDataManager(z3c.form.datamanager.AttributeField):
    """Datamanager which converts the list of keywords in the view into a
    set of keywords on the model."""

    def get(self):
        return sorted(super(KeywordDataManager, self).get(),
                      key=lambda x: x.title)

    def set(self, value):
        return super(KeywordDataManager, self).set(set(value))


class DeletePersonForm(icemac.addressbook.browser.base.BaseDeleteForm):
    label = _(u'Do you really want to delete this person?')
    interface = icemac.addressbook.interfaces.IPerson
    field_names = ('first_name', 'last_name')

    def _do_delete(self):
        try:
            super(DeletePersonForm, self)._do_delete()
        except gocept.reference.interfaces.IntegrityError:
            pass # XXX abort transaction (IntegrityError dooms it) and
                 # set notice using z3c.flashmessage


class PersonEntriesSource(
    zc.sourcefactory.contextual.BasicContextualSourceFactory):
    "Source to select entries from person."

    def getValues(self, context):
        for address in icemac.addressbook.address.address_mapping:
            for value in icemac.addressbook.sources.ContextByInterfaceSource(
                    address['interface']).factory.getValues(context):
                yield value
        for value in icemac.addressbook.sources.ContextByInterfaceSource(
            icemac.addressbook.file.interfaces.IFile).factory.getValues(
            context):
            yield value

    def getTitle(self, context, value):
        try:
            title_prefix = icemac.addressbook.address.object_to_title(value)
        except KeyError:
            # up to now there are only files besides the address entries
            title_prefix = _('file')
        title = icemac.addressbook.interfaces.ITitle(value)
        if title_prefix:
            title = '%s -- %s' % (title_prefix, title)
        return title


class IPersonEntries(zope.interface.Interface):
    """Content entries of an object."""

    entry = zope.schema.Choice(
        title=_(u'Entries'), source=PersonEntriesSource())


class DeleteSingleEntryForm(icemac.addressbook.browser.base.BaseEditForm):
    "Form to choose entry for deletion."

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

    @z3c.form.button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        self.status = self.noChangesMessage
