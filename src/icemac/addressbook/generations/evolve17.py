# -*- coding: latin-1 -*-
# Copyright (c) 2008-2014 Michael Howitz
# See also LICENSE.txt
# $Id$

import icemac.addressbook.generations.utils


def evolve(context):
    """Install `name` index.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
