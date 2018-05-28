from icemac.addressbook.i18n import _
import z3c.form.interfaces
import z3c.formui.interfaces
import z3c.layer.pagelet
import z3c.preference.interfaces
import zope.interface
import zope.viewlet.interfaces


class IAddressBookLayer(z3c.form.interfaces.IFormLayer,
                        z3c.layer.pagelet.IPageletBrowserLayer,
                        z3c.preference.interfaces.IPreferenceLayer):
    """Address book browser layer with form support."""


class IAddressBookBrowserSkin(z3c.formui.interfaces.IDivFormLayer,
                              IAddressBookLayer):
    """The address book browser skin using the div-based layout."""


class IPersonCount(zope.interface.Interface):
    """Number of persons for deletion."""

    count = zope.schema.Int(title=_(u'number of persons'), required=False)
    notes = zope.schema.TextLine(title=_(u'notes'), required=False)


class IErrorMessage(zope.interface.Interface):
    """Render error message human readable."""

    def __unicode__():
        """Return the translateable error text."""


class IDateWidget(z3c.form.interfaces.ITextWidget):
    """Special date widget to be able to use a JavaScript picker."""


class IDatetimeWidget(z3c.form.interfaces.ITextWidget):
    """Special date and time widget to be able to use a JavaScript picker."""


class ITimeWidget(z3c.form.interfaces.ITextWidget):
    """Special time widget to be able to use a JavaScript picker."""


class IImageSelectWidget(z3c.form.interfaces.ISelectWidget):
    """Select widget displays images as selectables."""


class IFanstaticViewletManager(zope.viewlet.interfaces.IViewletManager):
    """Manager those viewlets which `need()` fanstatic resources."""


class IAttributeTraversalHook(zope.interface.Interface):
    """Hook to be called when traversing an attribute.

    The traversed object and the request are taken to get the subscription
    adapters registered for this interface.

    """


class IIconProviderInfo(zope.interface.Interface):
    """Information about a someone whose icons are used in the address book."""

    name = zope.interface.Attribute('Name of the person or company')
    url = zope.interface.Attribute(
        'URL of the website the icons where taken from')


class IAddressBookBackground(zope.interface.Interface):
    """Marker for views which should display the address book background."""
