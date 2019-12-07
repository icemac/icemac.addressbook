import grokcore.component as grok
import icemac.addressbook.browser.menus.interfaces
import icemac.addressbook.interfaces
import itertools
import six
import z3c.menu.ready2go.checker
import z3c.menu.ready2go.manager
import zope.viewlet.manager
import zope.viewlet.viewlet


class MainMenuManager(z3c.menu.ready2go.manager.MenuManager):
    """MenuManager which filters out the deselected tabs."""

    outer_css_class = 'main-menu'
    inner_css_class = 'abmenu'

    def filter(self, viewlets):
        """Filter out deselected tabs."""
        viewlets = super(MainMenuManager, self).filter(viewlets)
        address_book = icemac.addressbook.interfaces.IAddressBook(None, None)
        try:
            deselected_tabs = address_book.deselected_tabs
        except AttributeError:
            deselected_tabs = []
        for name, viewlet in viewlets:
            if name not in deselected_tabs:
                yield name, viewlet


MainMenu = zope.viewlet.manager.ViewletManager(
    'main-menu', icemac.addressbook.browser.menus.interfaces.IMainMenu,
    bases=(MainMenuManager,))


def getWeight(arg):
    name, viewlet = arg
    view_name = viewlet.viewName
    assert view_name.startswith('@@')
    view_name = view_name[2:]
    view = zope.component.getMultiAdapter(
        (viewlet.context, viewlet.request), name=view_name)
    interface = getattr(view, 'interface', None)
    if interface is None:
        interface = getattr(view, 'interface_for_menu', None)
    assert interface is not None, (
        'View %r does neither have a non-null value on `interface` nor '
        'on `interface_for_menu` attribute. But this is needed to compute '
        'the AddMenu contents.' % view)
    entity = icemac.addressbook.interfaces.IEntity(interface)
    order = zope.component.getUtility(
        icemac.addressbook.interfaces.IEntityOrder)
    try:
        return order.get(entity)
    except (KeyError, zope.component.ComponentLookupError):
        # The entity is not known in the order or we are outside an address
        # book.
        return 0


class OrdersWeightMenuManager(z3c.menu.ready2go.manager.MenuManager):
    """Menu manager which uses address_book.orders as weight."""

    def sort(self, viewlets):
        return sorted(viewlets, key=getWeight)


class EmptyViewlet(zope.viewlet.viewlet.ViewletBase):
    """Helper class for AlwaysRenderTemplateManager."""


EMPTY_VIEWLET = EmptyViewlet(None, None, None, None)


class AlwaysRenderTemplateManager(OrdersWeightMenuManager):
    """Manager rendering template even there are no viewlets."""

    def update(self):
        super(AlwaysRenderTemplateManager, self).update()
        self.have_viewlets = bool(self.viewlets)
        if not self.have_viewlets:
            # Trick our `render` method to render manager's template which
            # should check `self.have_viewlets` to not render the empty
            # viewlet.
            self.viewlets.append(EMPTY_VIEWLET)


AddMenu = zope.viewlet.manager.ViewletManager(
    'add-menu', icemac.addressbook.browser.menus.interfaces.IAddMenu,
    bases=(AlwaysRenderTemplateManager,))


class SelectMenuItemOn(object):
    """Subscription adapter factory

    Returns interfaces or names of views for which a specific menu item in the
    main menu should be selected.

    Expects view names without `@@`.
    Example usage::

      my_search_views = SelectMenuItemOn('foosearch.html', IMyObject)

      <subscriber
         for="*"
         provides=".interfaces.ISearchMenuItemOn"
         factory=".my_search_views" />
    """

    def __init__(self, *items):
        self.items = items

    def __call__(self, *args):
        return self.items


class SubscriberSelectedChecker(
        z3c.menu.ready2go.checker.ViewNameSelectedChecker,
        grok.MultiAdapter):
    """Selected checker using a subscription adapter to check view names.

    In subclass as a ``grok.adapts`` statement like this::

        grok.adapts(zope.interface.Interface,
                    icemac.addressbook.browser.interfaces.IAddressBookLayer,
                    zope.interface.Interface,
                    icemac.addressbook.browser.menus.menu.MainMenu,
                    <concrete menu item class>)
    """

    subscriber_interface = NotImplemented
    grok.baseclass()

    @property
    def selected(self):
        if super(SubscriberSelectedChecker, self).selected:
            return True
        view_name = self.view.__name__
        context = self.context
        items = zope.component.subscribers((self,), self.subscriber_interface)
        for item in itertools.chain(*items):
            if isinstance(item, six.string_types):
                if view_name == item:
                    return True
            # If item is no view name it has to be an interface:
            elif item.providedBy(context):
                return True
        return False
