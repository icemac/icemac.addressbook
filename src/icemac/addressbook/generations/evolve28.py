# Copyright (c) 2008-2014 Michael Howitz
# See also LICENSE.txt
import icemac.addressbook.generations.utils
import icemac.addressbook.interfaces
import zope.annotation.interfaces
import zope.component
import zope.interface
import zope.location


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(ab):
    """Fix selected startpage after adding by default to view names.

    """
    startpage_view = ab.startpage[1]
    if startpage_view is not None and startpage_view.startswith('@@'):
        ab.startpage = (ab.startpage[0], ab.startpage[1][2:])
