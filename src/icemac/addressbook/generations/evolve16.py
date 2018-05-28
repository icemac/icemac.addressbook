import icemac.addressbook.generations.utils

# needed to make sure this package still exists and the instances get
# converted to the new class path
import zope.app.authentication

a = zope.app.authentication


def evolve(context):
    """Update the authentication utility."""
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
