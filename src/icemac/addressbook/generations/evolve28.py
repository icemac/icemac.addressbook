import icemac.addressbook.generations.utils


@icemac.addressbook.generations.utils.evolve_addressbooks
def evolve(ab):
    """Fix selected startpage after adding by default to view names."""
    startpage_view = ab.startpage[1]
    if startpage_view is not None and startpage_view.startswith('@@'):
        ab.startpage = (ab.startpage[0], ab.startpage[1][2:])
