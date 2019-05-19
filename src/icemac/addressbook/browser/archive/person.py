from icemac.addressbook.browser.person.person import DefaultSelectGroup
import icemac.addressbook.browser.person.person
import icemac.addressbook.browser.resource


class ArchivedPersonForm(
        icemac.addressbook.browser.person.person.PersonEditForm):
    """View the archived person."""

    title = icemac.addressbook.browser.breadcrumb.DO_NOT_SHOW

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
                'hint': widget.label,
                'value': widget.render()}

    def unarchive_url(self):
        return self.url(self.context, 'unarchive.html')
