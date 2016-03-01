# -*- coding: latin-1 -*-
import icemac.addressbook.generations.utils


generation = 3


def evolve(context):
    """Install the authentication utility."""
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
