# Copyright (c) 2008-2013 Michael Howitz
# See also LICENSE.txt
# $Id$

import icemac.addressbook.generations.utils


def evolve(context):
    """Install update default preferences to get time zone in.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
