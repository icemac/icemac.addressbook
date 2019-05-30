from icemac.addressbook.browser.person.person import DefaultSelectGroup
from icemac.addressbook.i18n import _
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

    def unarchive_url(self):
        return self.url(self.context, 'unarchive.html')
