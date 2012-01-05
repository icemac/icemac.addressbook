# -*- coding: latin-1 -*-
# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id$

__docformat__ = "reStructuredText"


import icemac.addressbook.generations.utils


generation = 9


def evolve(context):
    """Install orders utility.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
