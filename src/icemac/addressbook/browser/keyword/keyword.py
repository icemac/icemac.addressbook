from icemac.addressbook.i18n import _
import gocept.reference.interfaces
import grokcore.component as grok
import icemac.addressbook.browser.base
import icemac.addressbook.browser.breadcrumb
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.menus.menu
import icemac.addressbook.browser.metadata
import icemac.addressbook.browser.table
import icemac.addressbook.interfaces
import z3c.form.button
import z3c.table.column
import zope.interface


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class AddForm(icemac.addressbook.browser.base.BaseAddForm):

    title = _(u'Add new keyword')
    interface = icemac.addressbook.interfaces.IKeyword
    class_ = icemac.addressbook.keyword.Keyword
    next_url = 'parent'


def can_delete_keyword(form):
    """Button condition telling if the displayed keyword is deleteable."""
    return (
        icemac.addressbook.browser.base.can_access('delete.html')(form) and
        not gocept.reference.interfaces.IReferenceTarget(
            form.context).is_referenced())


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class EditForm(icemac.addressbook.browser.base.GroupEditForm):

    title = _(u'Edit keyword')
    groups = (icemac.addressbook.browser.metadata.MetadataGroup,)
    interface = icemac.addressbook.interfaces.IKeyword
    next_url = 'parent'
    z3c.form.form.extends(icemac.addressbook.browser.base.GroupEditForm,
                          ignoreFields=True)

    def applyChanges(self, data):
        # GroupForm has its own applyChanges but we need the one from
        # _AbstractEditForm here as inside the goups no changes are made but
        # there is a subscriber which raises an error which is handled by
        # _AbstractEditForm.
        return icemac.addressbook.browser.base._AbstractEditForm.applyChanges(
            self, data)

    @z3c.form.button.buttonAndHandler(
        _(u'Delete'), name='delete', condition=can_delete_keyword)
    def handleDelete(self, action):
        self.redirect_to_next_url('object', 'delete.html')


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class DeleteForm(icemac.addressbook.browser.base.BaseDeleteForm):
    """Delete a keyword after are-you-sure question."""

    title = _('Delete keyword')
    label = _('Do you really want to delete this keyword?')
    interface = icemac.addressbook.interfaces.IKeyword
    field_names = ('title', )


class KeywordContainerBreadCrumb(
        icemac.addressbook.browser.breadcrumb.MasterdataChildBreadcrumb):
    """Breadcrumb for keywords container."""

    grok.adapts(
        icemac.addressbook.interfaces.IKeywords,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _('Keywords')


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class Table(icemac.addressbook.browser.table.Table):
    """List keywords in address book."""

    title = icemac.addressbook.browser.breadcrumb.DO_NOT_SHOW
    no_rows_message = _(u'No keywords defined yet.')

    def setUpColumns(self):
        """Return the previously computed columns."""
        return [z3c.table.column.addColumn(
            self, icemac.addressbook.browser.table.TitleLinkColumn, 'keyword',
            header=_(u'keyword')),
        ]

    @property
    def values(self):
        """The values are stored on the context."""
        return self.context.get_keywords()


keyword_views = icemac.addressbook.browser.menus.menu.SelectMenuItemOn(
    icemac.addressbook.interfaces.IKeyword,
    icemac.addressbook.interfaces.IKeywords, 'addKeyword.html')
