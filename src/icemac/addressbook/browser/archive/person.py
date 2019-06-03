from icemac.addressbook.browser.person.person import DefaultSelectGroup
from icemac.addressbook.i18n import _
import icemac.addressbook.browser.base
import icemac.addressbook.browser.person.person
import icemac.addressbook.browser.resource
import z3c.form.group


class ArchivalData(z3c.form.group.Group):
    """Group rendering the archival data."""

    label = _('Archival data')
    fields = z3c.form.field.Fields(icemac.addressbook.interfaces.IArchivalData)


class ArchivedPersonForm(
        icemac.addressbook.browser.person.person.PersonEditForm):
    """View the archived person."""

    title = icemac.addressbook.browser.breadcrumb.DO_NOT_SHOW

    def __init__(self, context, request):
        super(ArchivedPersonForm, self).__init__(context, request)
        self.groups += (ArchivalData, )

    def update(self):
        icemac.addressbook.browser.resource.bootstrap.need()
        super(ArchivedPersonForm, self).update()

    def person_data(self):
        for group in self.groups:
            if isinstance(group, DefaultSelectGroup):
                continue
            yield {
                'label': group.label,
                'metadata': [
                    self._get_data(md_group.widgets.get(md_id))
                    for md_group in group.groups
                    for md_id in md_group.fields],
                'data': [
                    self._get_data(group.widgets.get(id))
                    for id, field in group.fields.items()
                ]
            }

    def _get_data(self, widget):
        return {'label': widget.label,
                'hint': widget.title,
                'value': widget.render()}

    def can_unarchive(self):
        return icemac.addressbook.browser.base.can_access_uri_part(
            self.context, self.request, 'unarchive.html')

    def unarchive_url(self):
        return self.url(self.context, 'unarchive.html')


class UnarchivePersonForm(icemac.addressbook.browser.base._BaseConfirmForm):
    """Move a person out of the archive after confirmation."""

    title = _('Unarchive person')
    label = _('Do you really want to unarchive this person?'
              ' Afterwards the person is no longer in the archive.'
              ' Editing and finding using searches is possible again.')
    cancel_status_message = _('Unarchiving canceled.')
    interface = icemac.addressbook.interfaces.IPerson
    field_names = ('first_name', 'last_name')
    z3c.form.form.extends(
        icemac.addressbook.browser.base._BaseConfirmForm, ignoreFields=True)

    @z3c.form.button.buttonAndHandler(_(u'Yes, unarchive'), name='action')
    def handleAction(self, action):
        self.status = _(
            '"${title}" unarchived.',
            mapping={
                'title': icemac.addressbook.interfaces.ITitle(
                    self.getContent())})
        self.redirect_to_next_url('parent')
        self.context.unarchive()
