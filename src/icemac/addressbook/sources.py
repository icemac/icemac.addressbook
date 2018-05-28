"""Module containing sources which are independent from interfaces.

Other sources are defined in interfaces.py to avoid circular references.

"""
from icemac.addressbook.i18n import _
import collections
import zc.sourcefactory.basic
import zope.component
import zope.component.hooks
import zope.globalrequest


class TitleMappingSource(zc.sourcefactory.basic.BasicSourceFactory):
    """Abstract base for sources using a mapping between value and title."""

    _mapping = None  # collections.OrderedDict, to be set in child class

    def getValues(self):
        return self._mapping.keys()

    def getTitle(self, value):
        return self._mapping[value]


class YesNoSource(TitleMappingSource):
    _mapping = collections.OrderedDict(
        ((True, _(u'yes')),
         (False, _(u'no'))))


yes_no_source = YesNoSource()


class AscDescSource(TitleMappingSource):
    _mapping = collections.OrderedDict(
        (('ascending', _(u'ascending (A-->Z)')),
         ('descending', _(u'descending (Z-->A)'))))


asc_desc_source = AscDescSource()


class FieldTypeSource(TitleMappingSource):
    _mapping = collections.OrderedDict(
        ((u'Bool', _(u'bool')),
         (u'Choice', _('choice')),
         (u'Date', _(u'date')),
         (u'Datetime', _(u'datetime')),
         (u'Decimal', _('decimal number')),
         (u'Int', _(u'integer number')),
         (u'Text', _(u'text area')),
         (u'TextLine', _(u'text line')),
         (u'Time', _(u'time')),
         (u'URI', _(u'URL')),
         ))


class SiteMenuSource(zc.sourcefactory.basic.BasicSourceFactory):
    """Source containing items of a z3c.menu.ready2go.ISiteMenu."""

    def __init__(self, view_class, menu_manager_class):
        self.menu_manager_class = menu_manager_class
        self.view_class = view_class

    @property
    def menu_manager(self):
        request = zope.globalrequest.getRequest()
        context = zope.component.hooks.getSite()
        view = self.view_class(context, request)
        menu_manager = self.menu_manager_class(context, request, view)
        menu_manager.update()
        return menu_manager

    def getValues(self):
        return self.menu_manager.viewlets

    def getTitle(self, value):
        return value.title

    def getToken(self, value):
        return value.url
