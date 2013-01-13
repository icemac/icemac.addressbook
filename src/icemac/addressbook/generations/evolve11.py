# -*- coding: latin-1 -*-
# Copyright (c) 2008-2013 Michael Howitz
# See also LICENSE.txt
# $Id$

import icemac.addressbook.generations.utils


def evolve(context):
    """Install batch size in default preferences provider.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
