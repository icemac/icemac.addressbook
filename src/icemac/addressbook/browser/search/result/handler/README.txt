===================================
Writing a new search result handler
===================================

1. Writing a search result handler
==================================

Search result handlers are views on the address book.  They can expect to
find the ids of the selected persons from the search result in a session key
named `person_ids`.


2. Adding it to the search result handler source
================================================

Objects returned by this source are listed in the drop-down "Handle selected
persons with".

The source lists the contents of the `ISearchResultHandlers` menu.  To
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

The permission might be different for handlers which are able to change
data.