# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.i18n import _
import icemac.addressbook.entities
import icemac.addressbook.sources
import stabledict
import zc.sourcefactory.basic


def tokenize(entity, field_name):
    "Convert an entity and a field_name into a unique string token."
    return "%s###%s" % (entity.name, field_name)


def untokenize(token):
    "Convert a token containing of entity and field name back to the objects."
    entity_name, field_name = token.split('###')
    entity = icemac.addressbook.interfaces.IEntity(entity_name)
    field = entity.getRawField(field_name)
    return entity, field


class ColumnSource(zc.sourcefactory.basic.BasicSourceFactory):
    "Columns in the person list."

    def getValues(self):
        # The main entities (the ones with default values on the
        # person) can be displayed in the person list.
        for entity in icemac.addressbook.entities.get_main_entities():
            # All fields, even the user defined ones, can be selected
            # as display columns.
            for field_name, field in entity.getRawFields():
                # We return a representation here which can be stored
                # in ZODB even though it is not so easy to compute a
                # title from it. But it woulod be more difficult to
                # adapt zope.preference to store this string instead
                # of field objects.
                yield tokenize(entity, field_name)

    def getTitle(self, value):
        entity, field = untokenize(value)
        # The titles might be message ids so allow to translate them.
        return _(u"${prefix} -- ${title}", mapping=dict(
            prefix=entity.title, title=field.title))


column_source = ColumnSource()


class AscDescSource(icemac.addressbook.sources.TitleMappingSource):
    _mapping = stabledict.StableDict(
        (('ascending', _(u'ascending (A-->Z)')),
         ('descending', _(u'descending (Z-->A)'))))

asc_des_csource = AscDescSource()
