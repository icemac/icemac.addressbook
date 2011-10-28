# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import _
import icemac.addressbook.fieldsource
import icemac.addressbook.sources
import zope.interface
import zope.schema


class IPersonList(zope.interface.Interface):
    """Person list preferences."""

    columns = zope.schema.List(
        title=_('columns'), required=True,
        value_type=zope.schema.Choice(
            title=_('columns'),
            source=icemac.addressbook.fieldsource.source))

    order_by = zope.schema.Choice(
        title=_('order by'),
        source=icemac.addressbook.fieldsource.source)

    sort_direction = zope.schema.Choice(
        title=_('sort direction'),
        source=icemac.addressbook.sources.asc_desc_source)

    batch_size = zope.schema.Int(title=_('batch size'), min=1)
