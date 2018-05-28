# -*- coding: latin-1 -*-
import icemac.addressbook.generations.utils


generation = 7


def evolve(context):
    """Install user defined fields utility.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
