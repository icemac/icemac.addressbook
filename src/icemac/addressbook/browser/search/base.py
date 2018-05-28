# -*- coding: utf-8 -*-
from icemac.addressbook.i18n import _
import icemac.addressbook.browser.interfaces
import icemac.addressbook.browser.search.interfaces
import z3c.form.button
import z3c.form.field
import z3c.formui.form
import zope.interface


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class Search(object):
    """View to select a search."""

    title = _('Search')
    show_headline = True
    form_explanation = u''


@zope.interface.implementer(
    icemac.addressbook.browser.interfaces.IAddressBookBackground)
class BaseView(zope.publisher.browser.BrowserView):
    """Base class for search views.

    Needs to extend from `zope.publisher.browser.BrowserView` as otherwise
    no search result handler can be found (the machinery expects this view
    to provide IBrowserView).

    """

    title = u'👉 set `title` in the subclass'
    form_explanation = u''  # description of the search form displayed below it

    search_params = None
    show_headline = False

    @property
    def result(self):
        if not self.search_params:
            return
        return self.search()

    def search(self):
        search = icemac.addressbook.browser.search.interfaces.ISearch(self)
        return search.search(**self.search_params)


class BaseSearchForm(z3c.formui.form.Form):
    """Base class for the search form."""

    interface = NotImplemented  # to be set in child class

    ignoreContext = True
    formErrorsMessage = _('There were some errors.')

    @property
    def fields(self):
        return z3c.form.field.Fields(self.interface)

    @z3c.form.button.buttonAndHandler(_('Search'), name='search')
    def search(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.__parent__.search_params = data


@zope.interface.implementer(
    icemac.addressbook.browser.search.interfaces.ISearch)
class BaseSearch(object):
    """Base class for search adapter."""

    def __init__(self, *args):
        pass

    def search(self, **kw):
        raise NotImplementedError()
