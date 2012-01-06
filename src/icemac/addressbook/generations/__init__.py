# Copyright (c) 2008-2012 Michael Howitz
# See also LICENSE.txt
# $Id$
"""Database initialisation and upgrading."""

import zope.generations.generations


GENERATION = 23


manager = zope.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.addressbook.generations')
