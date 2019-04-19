import icemac.addressbook.generations.utils


def evolve(context):
    """Install the person archive."""
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
