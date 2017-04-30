from icemac.addressbook.i18n import _
import icemac.addressbook.metadata.interfaces
import z3c.form.field
import z3c.form.group
import z3c.form.interfaces
import zope.component
import zope.dublincore.interfaces
import zope.preference.interfaces


class MetadataBaseGroup(z3c.form.group.Group):
    """Base class for groups displaying meta data information."""

    label = _('metadata')
    mode = z3c.form.interfaces.DISPLAY_MODE
    fields = NotImplemented

    def updateWidgets(self):
        """See interfaces.IForm"""
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()),
            z3c.form.interfaces.IWidgets)
        for attrName in ('ignoreRequest', 'ignoreContext', 'ignoreReadonly'):
            value = getattr(self.parentForm.widgets, attrName)
            setattr(self.widgets, attrName, value)
        # we need the value from the group here, not the one from the
        # parent form
        self.widgets.mode = self.mode
        self.widgets.update()


class MetadataGroup(MetadataBaseGroup):
    """Group displaying all meta data information."""

    fields = z3c.form.field.Fields(
        icemac.addressbook.metadata.interfaces.IEditor).select('creator')
    fields += z3c.form.field.Fields(
        zope.dublincore.interfaces.IDCTimes).select('created')
    fields += z3c.form.field.Fields(
        icemac.addressbook.metadata.interfaces.IEditor).select('modifier')
    fields += z3c.form.field.Fields(
        zope.dublincore.interfaces.IDCTimes).select('modified')


def timezone_messageid_factory(message_id):
    """Set currently selected time zone in the mapping of the message id."""
    def factory(ignored):
        prefs = zope.component.getUtility(
            zope.preference.interfaces.IPreferenceGroup, name="ab.timeZone")
        return _(message_id, mapping=dict(timezone=prefs.time_zone))
    return factory


ModifiedLabel = z3c.form.widget.ComputedWidgetAttribute(
    timezone_messageid_factory(_(u'Modification Date (${timezone})')),
    field=zope.dublincore.interfaces.IDCTimes['modified'])

ModifiedHint = z3c.form.widget.StaticWidgetAttribute(
    _(u'The date and time that the object was last modified converted to '
      u'the displayed time zone.'),
    field=zope.dublincore.interfaces.IDCTimes['modified'])

CreatedLabel = z3c.form.widget.ComputedWidgetAttribute(
    timezone_messageid_factory(_(u'Creation Date (${timezone})')),
    field=zope.dublincore.interfaces.IDCTimes['created'])

CreatedHint = z3c.form.widget.StaticWidgetAttribute(
    _(u'The date and time that the object was created converted to '
      u'the displayed time zone.'),
    field=zope.dublincore.interfaces.IDCTimes['created'])

MetadataGroupFieldsNotRequired = z3c.form.widget.StaticWidgetAttribute(
    False,
    view=MetadataGroup)
