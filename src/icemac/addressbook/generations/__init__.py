# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$
"""Database initialisation and upgrading."""

import zope.app.generations.generations


GENERATION = 7


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.addressbook.generations')
