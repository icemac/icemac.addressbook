# Copyright (c) 2008-2014 Michael Howitz
# See also LICENSE.txt
# $Id$

import icemac.addressbook.generations.utils


def evolve(context):
    """Install local principal annotation utility.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
