===================================
Writing a new search result handler
===================================

1. Writing a search result handler
==================================

Search result handlers are views on the address book.  They can expect to
find the ids of the selected persons from the search result in a session key
named `person_ids`.

You should use ``.base.Base`` as a base class for your search result handler.
The session can be accessed using the ``session`` property on this class.


2. Adding it to the search result handler source
================================================

Objects returned by this source are listed in the drop-down `Apply on
selected persons`.

The source lists the contents of the ``ISearchResultHandlers`` menu.  To
register an item for this menu you have to register it using ZCML like
this::


  <z3c:siteMenuItem
     manager="icemac.addressbook.browser.search.result.handler.manager.ISearchResultHandlers"
     layer="icemac.addressbook.browser.interfaces.IAddressBookLayer"
     name="<INTERNAL NAME OF HANDLER>"
     title="<I18N MESSAGE ID TO SHOW UP IN DROP-DOWN>"
     viewName="<NAME OF THE VIEW THE HANDLER IS REGISTERED WITH>"
     class="icemac.addressbook.browser.search.result.handler.manager.SearchResultHandler"
     permission="icemac.addressbook.ViewAddressBook"
     weight="<USED FOR SORTORDER>"
     />

Caution: `viewName` must not start with '@@'.

The permission might be different for handlers which are able to change
data.

3. Activate highlighting of the search menu entry
=================================================

To highlight the search menu entry in the main menu when your search result
handler is used, register the name of all views of your handler as
``ISearchMenuItemOn`` (without ``@@``!).
Example Python code of the subscription adapter::

    from icemac.addressbook.browser.menus.menu import SelectMenuItemOn
    my_handler_views = SelectMenuItemOn(
        ['my_handler.html', 'handler_2nd_view.html'])

  Example ZCML code to register the subscription adapter::

    <subscriber
       for="*"
       provides="icemac.addressbook.browser.search.interfaces.ISearchMenuItemOn"
       factory=".my_handler_views" />
