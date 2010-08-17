# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id$
"""Database initialisation and upgrading."""

import zope.app.generations.generations


GENERATION = 11


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.addressbook.generations')
