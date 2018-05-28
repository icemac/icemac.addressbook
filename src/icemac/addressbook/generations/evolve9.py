# -*- coding: latin-1 -*-
import icemac.addressbook.generations.utils


generation = 9


def evolve(context):
    """Install the orders utility."""
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
