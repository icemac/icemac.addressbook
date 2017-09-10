from icemac.addressbook.utils import dotted_name
import icemac.addressbook.browser.base
import zope.interface


def get_interfaces_flat(context):
    """Get a flat list of all interfaces provided by `context`."""
    return sorted(set([
        dotted_name(interface)
        for interface in zope.interface.implementedBy(
            context.__class__).flattened()] + [
        dotted_name(interface)
        for interface in zope.interface.directlyProvidedBy(
            context).flattened()]))


class Inspector(icemac.addressbook.browser.base.FlashView):
    """Inspect the current view or object."""

    title = u'Inspector'

    def show_context(self):
        yield {'key': 'context',
               'value': self.context}
        yield {'key': 'class of context',
               'value': self.context.__class__}
        yield {'key': 'base classes of context',
               'value': self.context.__class__.__bases__}

    def context_interfaces(self):
        return get_interfaces_flat(self.context)
