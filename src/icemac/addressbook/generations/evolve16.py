# -*- coding: latin-1 -*-
# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
import icemac.addressbook.generations.utils

# needed to make sure this package still exists and the instances get
# converted to the new class path
import zope.app.authentication

a = zope.app.authentication


def evolve(context):
    """Updates the authentication utility.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
