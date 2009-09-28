# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt
# $Id$
"""Database initialisation and upgrading."""

import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=5,
    generation=5,
    package_name='icemac.addressbook.generations')
