=================
 Create a search
=================

A search consists of:

- a form viewlet to enter the search terms

- an adapter to do the search

- a viewlet to display the results

- a view to display to display the search and result viewlets


The search view
===============

- There is a base view `.base.BaseView` which should be used as base
  class for the new search view.

- The view has to be registered as a pagelet using the template
  `search.pt`.  Example::

  <gocept:pagelet
     name="my_search.html"
     for="icemac.addressbook.interfaces.IAddressBook"
     permission="icemac.addressbook.ViewPerson"
     layer="icemac.addressbook.browser.interfaces.IAddressBookLayer"
     template="search.pt"
     class=".mySearch.SearchView"
     />

- To make the search accessible in the search menu, it must be
  registered with this menu. Example::

  <browser:viewlet
     manager="icemac.addressbook.browser.search.interfaces.ISearchMenu"
     name="My search"
     viewName="@@my_search.html"
     for="icemac.addressbook.interfaces.IAddressBook"
     class="z3c.menu.ready2go.item.ContextMenuItem"
     permission="icemac.addressbook.ViewPerson"
     layer="icemac.addressbook.browser.interfaces.IAddressBookLayer"
     weight="10"
     />

The form viewlet
================

- There is a base form `.base.BaseSearchForm` which requires to
  implement an interface those schema fields are displayed in the
  form.

- The viewlet must be registered for the search view. Example::

  <browser:viewlet
     manager="icemac.addressbook.browser.search.interfaces.ISearchForm"
     name="form"
     view=".my_search.SearchView"
     class=".my_search.SearchForm"
     permission="icemac.addressbook.ViewPerson"
     layer="icemac.addressbook.browser.interfaces.IAddressBookLayer"
     />

The search adapter
==================

- The adapter has to adapt the search view and provide
  `.interfaces.ISearch`.

- The `search` method of the adapter is called with the search form
  contents as keyword arguments.

- The `search` method must return an iterable of search results.


The result display viewlet
==========================

The result display viewlet calls the `result` property of the view.
When it is `None`, no search has been done yet, otherwise it returns
an iterable of the results. (The result viewlet must be able to handle
this.)

There are some pre-defined result viewlets:

- .result.simple.ExportForm + result/export.pt: simple table
  containing names of persons, export abilities. Example to register
  viewlet::

    <browser:viewlet
       manager="icemac.addressbook.browser.search.interfaces.ISearchResult"
       name="result_table"
       view=".my_search.SearchView"
       class=".result.simple.ExportForm"
       template="result/export.pt"
       permission="icemac.addressbook.ViewPerson"
       layer="icemac.addressbook.browser.interfaces.IAddressBookLayer"
       />

- result_person.pt: (template)
    simple list of found persons, no further actions possible


