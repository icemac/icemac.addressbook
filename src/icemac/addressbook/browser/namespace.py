import icemac.addressbook.browser.interfaces
import zope.component
import zope.traversing.namespace


class attr(zope.traversing.namespace.attr):
    """Specialized ++attribute++ traverser."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        target = super(attr, self).traverse(name, ignored)
        # Iterating the subscribers calls them:
        list(zope.component.subscribers(
            (target, self.request),
            icemac.addressbook.browser.interfaces.IAttributeTraversalHook))
        return target
