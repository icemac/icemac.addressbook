from icemac.addressbook.interfaces import IKeywords, IKeyword
from icemac.addressbook.keyword import Keyword, KeywordContainer
import icemac.addressbook.interfaces
import icemac.addressbook.keyword
import zope.event
import zope.lifecycleevent


def test_keyword__Keyword__1():
    """`Keyword` fulfills the `IKeyword` interface."""
    zope.interface.verify.verifyObject(IKeyword, Keyword())


def test_keyword__changed__1(address_book, PersonFactory, KeywordFactory):
    """It updates the keyword index if a keyword title was changed."""
    friends = KeywordFactory(address_book, u'friends')
    person = PersonFactory(
        address_book, u'Kohn', keywords=[u'church', friends])

    catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
    results = catalog.searchResults(keywords={'any_of': ('friends', )})
    assert 1 == len(results)
    assert list(results)[0] is person

    # When the title of a keyword has changed the index gets updated at the
    # modified event:
    friends.title = u'Freunde'
    attributes = zope.lifecycleevent.Attributes(
        icemac.addressbook.interfaces.IKeyword, 'title')
    event = zope.lifecycleevent.ObjectModifiedEvent(friends, attributes)
    zope.event.notify(event)
    assert 2 == catalog.get('keywords').wordCount.value
    results = catalog.searchResults(keywords={'any_of': ('Freunde', )})
    assert 1 == len(results)
    assert list(results)[0] is person


def test_keyword__changed__2(address_book, PersonFactory, KeywordFactory):
    """It doesn't update the keyword index if keyword title wasn't changed."""
    friends = KeywordFactory(address_book, u'friends')
    person = PersonFactory(
        address_book, u'Kohn', keywords=[u'church', friends])

    catalog = zope.component.getUtility(zope.catalog.interfaces.ICatalog)
    results = catalog.searchResults(keywords={'any_of': ('friends', )})
    assert 1 == len(results)
    assert list(results)[0] is person

    # When the title of a keyword has not changed the index gets not updated at
    # the modified event:
    attributes = zope.lifecycleevent.Attributes(
        icemac.addressbook.interfaces.IKeyword, 'descr')
    event = zope.lifecycleevent.ObjectModifiedEvent(friends, attributes)
    zope.event.notify(event)
    results = catalog.searchResults(keywords={'any_of': ('friends', )})
    assert 1 == len(results)
    assert list(results)[0] is person


def test_keyword__KeywordContainer__1():
    """`KeywordContainer` fulfills the `IKeywords` interface."""
    zope.interface.verify.verifyObject(IKeywords, KeywordContainer())


def test_keyword__KeywordContainer__get_keywords__1():
    """It returns an empty generator if the container is empty."""
    assert [] == list(KeywordContainer().get_keywords())


def test_keyword__KeywordContainer__get_keywords__2():
    """It returns the keywords in the container."""
    kc = KeywordContainer()
    kc['1'] = Keyword(u'qwe')
    kc['2'] = Keyword(u'asd')
    kc['3'] = Keyword(u'dfg')
    kc['4'] = Keyword(u'bgr')
    keyword_titles = sorted(x.title for x in kc.get_keywords())
    assert ['asd', 'bgr', 'dfg', 'qwe'] == keyword_titles


def test_keyword__KeywordContainer__get_keyword_by_title__1():
    """It returns a keyword with a matching title."""
    kc = KeywordContainer()
    kc['1'] = Keyword(u'foo')
    kc['2'] = Keyword(u'bar')
    assert kc['1'] == kc.get_keyword_by_title(u'foo')
    assert kc['2'] == kc.get_keyword_by_title(u'bar')


def test_keyword__KeywordContainer__get_keyword_by_title__2():
    """It returns `None` if the container is empty."""
    assert None is KeywordContainer().get_keyword_by_title(u'asdf')


def test_keyword__KeywordContainer__get_keyword_by_title__3():
    """It returns `None` if no matching keyword can be found."""
    kc = KeywordContainer()
    kc['1'] = Keyword(u'asdf')
    assert None is kc.get_keyword_by_title(u'foo')
    assert None is kc.get_keyword_by_title(u'bar')


def test_keyword__KeywordContainer__get_keyword_by_title__4():
    """It returns the default value if there is no keyword for title."""
    kc = KeywordContainer()
    kc['1'] = Keyword(u'asdf')
    assert 'baz' == kc.get_keyword_by_title(u'foo', 'baz')
