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

- Put the explanation of your search form on the `form_explanation` attribute
  of your child class of `.base.BaseView`. It will be displayed below the form.
  The view class does not need any further additions, but it is needed later on
  to register the viewlets for it.

- The view has to be registered as a pagelet using the template
  `search.pt`.  Example::

  <configure
     xmlns="http://namespaces.zope.org/zope"
     xmlns:browser="http://namespaces.zope.org/browser"
     xmlns:z3c="http://namespaces.zope.org/z3c"
     xmlns:gocept="http://namespaces.gocept.com/zcml">

    <gocept:pagelet
       for="icemac.addressbook.interfaces.IAddressBook"
       layer="icemac.addressbook.browser.interfaces.IAddressBookLayer"
       name="my_search.html"
       class=".mySearch.SearchView"
       template="search.pt"
       permission="icemac.addressbook.ViewPerson"
       />

- To make the search accessible in the search menu, it must be
  registered with this menu. Example::

  <z3c:contextMenuItem
     manager="icemac.addressbook.browser.search.interfaces.ISearchMenu"
     for="icemac.addressbook.interfaces.IAddressBook"
     layer="icemac.addressbook.browser.interfaces.IAddressBookLayer"
     name="My-search"
     title="My search"
     viewName="@@my_search.html"
     permission="icemac.addressbook.ViewPerson"
     weight="10"
     />

- To highlight the search menu item in the main menu when your search is used
  register the name of the view (without ``@@``!) as ``ISearchMenuItemOn``.
  Example Python code of the subscription adapter::

    from icemac.addressbook.browser.menus.menu import SelectMenuItemOn
    my_search_view = SelectMenuItemOn(['my_seach.html'])

  Example ZCML code to register the subscription adapter::

    <subscriber
       for="*"
       provides=".interfaces.ISearchMenuItemOn"
       factory=".my_search_view" />


The form viewlet
================

- There is a base form `.base.BaseSearchForm`. You only have to set the
  `interface` attribute on a sub class. It has to be an interface with
  schema fields which are displayed in the form.

- The viewlet must be registered for the search view. Example::

  <browser:viewlet
     manager="icemac.addressbook.browser.search.interfaces.ISearchForm"
     view=".my_search.SearchView"
     layer="icemac.addressbook.browser.interfaces.IAddressBookLayer"
     name="form"
     class=".my_search.SearchForm"
     permission="icemac.addressbook.ViewPerson"
    />

The search adapter
==================

- The adapter has to adapt the search view and provide
  `.interfaces.ISearch`. There is `.base.BaseSearch` which can be used as a
  base class.

- The `search` method of the adapter is called with the search form
  contents as keyword arguments.

- The `search` method must return an iterable of search results.

- Don't forget to register the adapter in ZCML.


The result display viewlet
==========================

The result display viewlet calls the `result` property of the (base)
view.  When it is `None`, no search has been done yet, otherwise it
returns an iterable of the results. (The result viewlet must be able
to handle this.)

There are some pre-defined result viewlets:

- `.result.simple.ExportForm`: simple table
  containing names of persons, export abilities. Example to register
  viewlet::

    <browser:viewlet
       manager="icemac.addressbook.browser.search.interfaces.ISearchResult"
       view=".my_search.SearchView"
       layer="icemac.addressbook.browser.interfaces.IAddressBookLayer"
       name="result_table"
       class=".result.simple.SimpleExportForm"
       permission="icemac.addressbook.ViewPerson"
      />

- `.result.personlist.ExportForm`: table containing the
  same columns like person list table (as defined in personal preferences of
  the user) + export abilities. Example to register viewlet::

    <browser:viewlet
       manager="icemac.addressbook.browser.search.interfaces.ISearchResult"
       view=".my_search.SearchView"
       layer="icemac.addressbook.browser.interfaces.IAddressBookLayer"
       name="result_table"
       class=".result.personlist.ExportForm"
       permission="icemac.addressbook.ViewPerson"
      />

Integration in address book
===========================

You have to include the ZCML file of your search in the address book's ZCML.

