from icemac.addressbook.i18n import _
import zope.interface
import zope.schema


class IEditor(zope.interface.Interface):
    """Editor properties."""

    creator = zope.schema.TextLine(
        title=_(u"creator"))

    modifier = zope.schema.TextLine(
        title=_(u"last modfier"))
