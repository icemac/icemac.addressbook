# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import _
import icemac.addressbook.preferences.sources
import zope.interface
import zope.schema


class IPersonList(zope.interface.Interface):
    "Person list preferences."

    columns = zope.schema.List(
        title=_('columns'), required=True,
        value_type=zope.schema.Choice(
            title=_('columns'),
            source=icemac.addressbook.preferences.sources.column_source))

    order_by = zope.schema.Choice(
        title=_('order by'),
        source=icemac.addressbook.preferences.sources.column_source)

    sort_direction = zope.schema.Choice(
        title=_('sort direction'),
        source=icemac.addressbook.preferences.sources.asc_des_csource)

    batch_size = zope.schema.Int(title=_('batch size'), min=1)
