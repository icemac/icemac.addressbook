# -*- coding: latin-1 -*-
import icemac.addressbook.generations.utils

generation = 1


def evolve(context):
    """Install the necessary components for address books."""
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
