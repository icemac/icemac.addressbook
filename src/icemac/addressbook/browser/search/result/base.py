# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
import icemac.addressbook.browser.base
import icemac.addressbook.browser.search.result.handler.manager
import z3c.form.button
import z3c.table.column
import zope.browserpage.viewpagetemplatefile
import zope.interface
import zope.schema


class ISearchResultHanderChoice(zope.interface.Interface):
    """Drop down to select search result handler."""

    search_result_handler = zope.schema.Choice(
        title=_(u'Apply on selected persons'),
        source=icemac.addressbook.browser.search.result.handler.manager.source)


class BaseSearchResultForm(icemac.addressbook.browser.base._AbstractEditForm):
    """Base form of search results allowing handling of results."""

    ignoreContext = True
    interface = ISearchResultHanderChoice
    template = zope.browserpage.viewpagetemplatefile.ViewPageTemplateFile(
        'result.pt')
    id = 'search-export-form'
    table_class = NotImplemented

    def renderTable(self):
        table = self.table_class(self.__parent__, self.request)
        table.update()
        return table.render()

    @z3c.form.button.buttonAndHandler(_('Apply'), name='apply')
    def callHandler(self, action):
        """Call the selected handler after storing data in session."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.session['person_ids'] = self.request.form.get('persons', ())

        # Fanstatic seems to have a problem with cookies and relative
        # redirects (a new cookie is set in this case), so we have to
        # redirect using an absolute URL.
        self.request.response.redirect(self.url(
            self.context, data['search_result_handler'].viewName))


class BasePersonTable(icemac.addressbook.browser.table.Table):
    """Base result table displaying at least a checkbox column (using ZCML)."""

    def update(self):
        self.result = self.context.result
        super(BasePersonTable, self).update()

    @property
    def values(self):
        return self.result


class CheckBoxColumn(z3c.table.column.CheckBoxColumn):
    """Table column to show checkboxes to select result rows for export."""

    weight = -1

    def renderHeadCell(self):
        return u'<input type="checkbox" class="checkall" checked="checked" />'

    def getItemKey(self, item):
        return 'persons:list'

    def isSelected(self, item):
        # The result is not persisted, so always use the default:
        return True
