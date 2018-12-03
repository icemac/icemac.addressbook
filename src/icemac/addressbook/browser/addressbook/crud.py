from icemac.addressbook.i18n import _
import grokcore.component as grok
import icemac.addressbook.addressbook
import icemac.addressbook.browser.base
import icemac.addressbook.browser.breadcrumb
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.menus.menu
import icemac.addressbook.browser.metadata
import icemac.addressbook.interfaces
import z3c.form.button
import zope.interface
import zope.size.interfaces


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class AddForm(icemac.addressbook.browser.base.BaseAddForm):

    title = _(u'Add new address book')
    interface = icemac.addressbook.interfaces.IAddressBook
    class_ = icemac.addressbook.addressbook.AddressBook
    next_url = 'object'

    def create(self, data):
        self.selected_time_zone = data.pop('time_zone')
        return super(AddForm, self).create(data)

    def add(self, obj):
        super(AddForm, self).add(obj)
        with zope.component.hooks.site(obj):
            obj.time_zone = self.selected_time_zone


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class EditForm(icemac.addressbook.browser.base.GroupEditForm):

    interface = icemac.addressbook.interfaces.IAddressBook
    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)
    next_url = 'object'
    next_view = 'edit-address_book.html'

    @z3c.form.button.buttonAndHandler(_('Save'), name='apply')
    def handleApply(self, action):
        super(EditForm, self).handleApply(self, action)

    @z3c.form.button.buttonAndHandler(
        _(u'Delete all persons in address book'), name='delete_content',
        condition=icemac.addressbook.browser.base.can_access(
            '@@delete-address_book-content.html'))
    def handleDeleteContent(self, action):
        self.redirect_to_next_url('object', 'delete-address_book-content.html')


class AddressbookEditBreadCrumb(
        icemac.addressbook.browser.breadcrumb.MasterdataChildBreadcrumb):
    """Breadcrumb for the edit view of the address book."""

    grok.adapts(
        EditForm,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _(u'Edit address book data')
    target_url = None


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class DeleteForm(icemac.addressbook.browser.base.BaseDeleteForm):
    """Delete whole address book."""

    title = _('Delete address book')
    label = _(u'Do you really want to delete this whole address book?')
    interface = icemac.addressbook.interfaces.IAddressBook
    field_names = ('title', )
    next_url_after_cancel = 'parent'

    def _do_delete(self):
        # delete users first
        principals = self.context.principals
        for name in list(principals.keys()):
            del principals[name]
        return super(DeleteForm, self)._do_delete()


@zope.component.adapter(icemac.addressbook.interfaces.IAddressBook)
@zope.interface.implementer(icemac.addressbook.browser.interfaces.IPersonCount)
class PersonCount(object):
    """Adapter to count persons in address book."""

    def __init__(self, address_book):
        basic_unit, self.count = zope.size.interfaces.ISized(
            address_book).sizeForSorting()
        self.notes = zope.i18n.translate(
            _(u'The users inside this address book will not get deleted.'),
            context=zope.globalrequest.getRequest())


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class DeleteContentForm(icemac.addressbook.browser.base.BaseDeleteForm):
    """Delete address book contents (aka persons)."""

    title = _('Delete all persons')
    label = _(
        u'Do you really want to delete all persons in this address book?')
    interface = icemac.addressbook.browser.interfaces.IPersonCount
    next_view = 'edit-address_book.html'

    def _handle_action(self):
        icemac.addressbook.browser.base.delete_persons(
            self.context, self.context.keys())
        self.status = _('Address book contents deleted.')
        self.redirect_to_next_url('object', 'person-list.html')


address_book_views = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    'edit-address_book.html', 'delete-address_book-content.html',
    'delete-address_book.html')
