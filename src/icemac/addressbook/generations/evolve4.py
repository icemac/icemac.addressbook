# -*- coding: latin-1 -*-
import zope.generations.utility


generation = 4


def evolve(context):
    """Update the root folder to be a ``zope.site.folder.Folder`` instead of

    ``zope.app.folder.folder.Folder``.
    """
    root = zope.generations.utility.getRootFolder(context)
    context.connection.root()._p_changed = True
    root._p_changed = True
