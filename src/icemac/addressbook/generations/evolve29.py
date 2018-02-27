import icemac.addressbook.generations.utils


def evolve(context):
    """Install the `schema_name` index."""
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
