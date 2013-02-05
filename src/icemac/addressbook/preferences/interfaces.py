# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Michael Howitz
# See also LICENSE.txt
from icemac.addressbook.i18n import _
import icemac.addressbook.fieldsource
import icemac.addressbook.sources
import pytz
import stabledict
import zope.interface
import zope.schema


class IPersonLists(zope.interface.Interface):
    """Person lists preferences."""

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


class IPersonListTab(zope.interface.Interface):
    """Preferences of the person list tab."""

    batch_size = zope.schema.Int(title=_('batch size'), min=1)


class TimeZones(icemac.addressbook.sources.TitleMappingSource):
    """Source of all available time zones."""

    _mapping = stabledict.StableDict(((x, x) for x in pytz.all_timezones))


class ITimeZone(zope.interface.Interface):
    """Preferred time zone."""

    time_zone = zope.schema.Choice(title=_('time zone'), source=TimeZones())
