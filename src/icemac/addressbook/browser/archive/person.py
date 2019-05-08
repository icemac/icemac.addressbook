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
                'metadata': [{
                    'label': md_group.widgets.get(md_id).label,
                    'value': md_group.widgets.get(md_id).render(),
                } for md_group in group.groups
                    for md_id, md_field in md_group.fields.items()],
                'data': [{
                    'label': field.field.title,
                    'hint': field.field.description,
                    'value': group.widgets.get(id).render(),
                } for id, field in group.fields.items()
                ]
            }

    def unarchive_url(self):
        return self.url(self.context, 'unarchive.html')
