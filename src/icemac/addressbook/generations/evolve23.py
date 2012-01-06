# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id$

import icemac.addressbook.generations.utils


def evolve(context):
    """Install update default preferences to new prefs structure.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
