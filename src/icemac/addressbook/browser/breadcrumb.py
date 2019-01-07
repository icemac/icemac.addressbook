# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
import grokcore.component as grok
import icemac.addressbook.browser.base
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.table
import z3c.layer.pagelet.interfaces
import zope.browser.interfaces
import zope.contentprovider.interfaces
import zope.contentprovider.provider
import zope.interface
import zope.location.interfaces
import zope.preference.interfaces
import zope.publisher.interfaces
import zope.schema
import zope.traversing.api

DO_NOT_SHOW = 'I do not want to show up as a breadcrumb!'


class IBreadcrumb(zope.interface.Interface):
    """A single breadcrumb which knows its parent."""

    show = zope.schema.Bool(title=u'Render this breadcrumb in front end?')
    title = zope.schema.TextLine(title=u'Title rendered in front end.')
    target_url = zope.schema.URI(
        title=u'Target URL or `None` for a text breadcrumb',
        required=False)
    parent = zope.schema.Object(
        zope.location.interfaces.ILocation,
        title=u'Object for the parent breadcrumb.',
        description=u'If `None`, no further parent exists.',
        required=False)

    def render():
        """Render the HTML of the breadcrumb."""


@zope.interface.implementer(IBreadcrumb)
class Breadcrumb(grok.MultiAdapter,
                 icemac.addressbook.browser.base.BaseView):
    """Base breadcrumb implementation."""

    grok.baseclass()
    grok.provides(IBreadcrumb)

    show = True
    template = ViewPageTemplateFile('breadcrumb.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def title(self):
        try:
            title = icemac.addressbook.interfaces.ITitle(self.context)
        except (zope.security.interfaces.ForbiddenAttribute,
                ValueError):  # pragma: no cover
            title = "{}: <unprintable title>".format(
                self.context.__class__.__name__)
        return title

    @property
    def target_url(self):
        return self.url(self.context)

    @property
    def parent(self):
        return zope.traversing.api.getParent(self.context)

    def __repr__(self):
        """Custom representation for breadcrumbs."""
        return '<{0}: {1.title!r}>'.format(
            icemac.addressbook.utils.dotted_name(self.__class__), self)

    def render(self):
        return self.template()


class DefaultBreadcrumb(Breadcrumb):
    """Most unspecific breadcrumb implementation. Used as fall back."""

    grok.adapts(
        zope.interface.Interface,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    target_url = None


class MasterdataChildBreadcrumb(Breadcrumb):
    """Breadcrumb those parent is `masterdata.html`."""

    grok.baseclass()

    @property
    def parent(self):
        return zope.component.getMultiAdapter(
            (icemac.addressbook.interfaces.IAddressBook(self.context),
             self.request),
            name='masterdata.html')


class ViewBreadcrumb(Breadcrumb):
    """Default breadcrumb implementation for views."""

    grok.adapts(
        icemac.addressbook.browser.base.FlashView,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    target_url = None

    @property
    def show(self):
        return self.title != DO_NOT_SHOW

    @property
    def title(self):
        try:
            title = self.context.title
        except AttributeError:
            title = None
        if title is None:
            # AttributeError above or not set:
            title = u'👉 missing title! 😱 {!r}'.format(self.context)
        return title


class TableBreadcrumb(ViewBreadcrumb):
    """View for views based on the `Table` class and its subclasses."""

    grok.adapts(
        icemac.addressbook.browser.table.Table,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)


class RootBreadcrumb(Breadcrumb):
    """Breadcrumb for the root folder: Hide it."""

    grok.adapts(
        zope.site.interfaces.IRootFolder,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    show = False


class ModelBreadcrumb(Breadcrumb):
    """Default breadcrumb implementation for model objects."""

    grok.adapts(
        zope.location.interfaces.ILocation,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)


class PersonEntityBreadcrumb(Breadcrumb):
    """Do not render addresses ansd numbers as breadcrumbs.

    They do not have a default view and their only view is the delete view
    which renders the relevant information.
    """

    grok.adapts(
        icemac.addressbook.interfaces.IPersonEntity,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    show = False


class PreferenceCategoryBreadcrumb(Breadcrumb):
    """Breadcrumb for preference categories."""

    grok.adapts(
        zope.preference.interfaces.IPreferenceCategory,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    title = _('Preferences')

    @property
    def parent(self):
        return icemac.addressbook.interfaces.IAddressBook(self.context)

    @property
    def target_url(self):
        return self.url(self.parent, '++preferences++/ab')


class PreferenceGroupBreadcrumb(PreferenceCategoryBreadcrumb):
    """Breadcrumb for /++preferences++/ --> hide."""

    grok.adapts(
        zope.preference.interfaces.IPreferenceGroup,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    show = False


class SystemErrorViewBreadcrumb(Breadcrumb):
    """Breadcrumb to render a title for system error views."""

    grok.adapts(
        zope.browser.interfaces.ISystemErrorView,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    target_url = None
    title = 'SystemError'


class UnauthorizedPageletBreadcrumb(Breadcrumb):
    """Do not render a breadcrumb for the unauthorized pagelet."""

    grok.adapts(
        z3c.layer.pagelet.interfaces.IUnauthorizedPagelet,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    show = False

    @property
    def parent(self):
        return icemac.addressbook.interfaces.IAddressBook(self.context)


class NotFoundPageletBreadcrumb(Breadcrumb):
    """Do not render a breadcrumb for the not found pagelet."""

    grok.adapts(
        z3c.layer.pagelet.interfaces.INotFoundPagelet,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    show = False


class NotFoundBreadcrumb(Breadcrumb):
    """Breadcrumb to render a title for the NotFound exception."""

    grok.adapts(
        zope.publisher.interfaces.INotFound,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    target_url = None
    title = _('Not Found')


class EntityBreadcrumb(Breadcrumb):
    """Breadcrumb for an entity."""

    grok.adapts(
        icemac.addressbook.interfaces.IEntity,
        icemac.addressbook.browser.interfaces.IAddressBookLayer)

    @property
    def parent(self):
        return zope.component.getUtility(
            icemac.addressbook.interfaces.IEntities)


class BreadcrumbContentProvider(
        grok.MultiAdapter,
        zope.contentprovider.provider.ContentProviderBase):
    """Content provider rendering the breadcrumbs."""

    grok.adapter(
        zope.interface.Interface,
        icemac.addressbook.browser.interfaces.IAddressBookLayer,
        zope.interface.Interface)
    grok.provides(zope.contentprovider.interfaces.IContentProvider)
    grok.name('breadcrumbs')

    def render(self):
        return '\n'.join(self.rendered_breadcrumbs)

    @property
    def rendered_breadcrumbs(self):
        for bc in reversed(list(self.reversed_breadcrumbs)):
            yield bc.render()

    @property
    def reversed_breadcrumbs(self):
        bc = self.get_breadcrumb(self.__parent__)
        parent = bc.parent
        while parent is not None:
            if bc.show:
                yield bc
            bc = self.get_breadcrumb(parent)
            parent = bc.parent
        assert not bc.show, 'Found a root breadcrumb with show = True'

    def get_breadcrumb(self, context):
        return zope.component.getMultiAdapter(
            (context, self.request), IBreadcrumb)
