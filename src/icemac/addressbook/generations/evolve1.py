# -*- coding: latin-1 -*-
# Copyright (c) 2008-2014 Michael Howitz
# See also LICENSE.txt
# $Id$

__docformat__ = "reStructuredText"

import zope.generations.utility

import icemac.addressbook.interfaces
import icemac.addressbook.person
import icemac.addressbook.generations.utils

generation = 1

person_created_with_set_site = icemac.addressbook.utils.set_site(
    icemac.addressbook.person.person_created)


def evolve(context):
    """Installs the necessary components for address books.

    Defines references on persons.
    """

    root = zope.generations.utility.getRootFolder(context)
    # persons need gocept.reference which needs a local utility stored in root

    # persons
    persons = zope.generations.utility.findObjectsProviding(
        root, icemac.addressbook.interfaces.IPerson)
    for person in persons:
        person_created_with_set_site(root, person, None)

    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
