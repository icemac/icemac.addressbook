import icemac.addressbook.conftest
import icemac.addressbook.interfaces
import mock
import pytest
import transaction
import zope.component
import zope.component.hooks


# Fixtures to set-up infrastructure which are usable in tests:

@pytest.yield_fixture(scope='function')
def mailto_data(mailtoDataS):
    """Make a stacked demo storage on search data."""
    mailToConnectionS, persons = mailtoDataS
    for connection in icemac.addressbook.conftest.pyTestStackDemoStorage(
            mailToConnectionS.zodb, 'MailToFunction'):
        yield persons


# Infrastructure fixtures


@pytest.yield_fixture(scope='session')
def mailtoDataS(addressBookS, KeywordFactory, PersonFactory,
                EMailAddressFactory, FullPersonFactory):
    """Create data used in mail-to tests."""
    kws = [u'mail-me']
    for connection in icemac.addressbook.conftest.pyTestStackDemoStorage(
            addressBookS, 'MailToSession'):
        for address_book in icemac.addressbook.conftest.site(connection):
            persons = {}
            # No EMailAddress object
            persons['p0'] = PersonFactory(
                address_book, u'No Mail', keywords=kws)
            persons['p1'] = PersonFactory(address_book, u'Mail', keywords=kws)
            EMailAddressFactory(
                persons['p1'], u'icemac@example.net', set_as_default=True)
            persons['p2'] = PersonFactory(
                address_book, u'Mail Too', keywords=kws)
            EMailAddressFactory(
                persons['p2'], u'mail@example.com', set_as_default=True)
            persons['p3'] = PersonFactory(
                address_book, u'Double Mail', keywords=kws)
            # Dulicate email address
            EMailAddressFactory(
                persons['p3'], u'mail@example.com', set_as_default=True)
            persons['p4'] = FullPersonFactory(
                address_book, u'Other Mail', keywords=kws)
            # default email address is None
            EMailAddressFactory(
                persons['p4'], u'other@example.com', set_as_default=False)
            transaction.commit()
            yield connection, persons


# Tests

def test_mailto__MailTo__unique_mail_addresses__1(mailto_data):
    """It is a sorted list of unique email addresses."""
    from .mailto import MailTo
    from gocept.testing.mock import Property
    view = MailTo()
    view.request = mock.Mock()
    persons = ('icemac.addressbook.browser.search.result.handler.mailto.'
               'mailto.MailTo.persons')
    with mock.patch(persons, Property()) as persons,\
            zope.component.hooks.site(mailto_data['p0'].__parent__):
        persons.return_value = [mailto_data[x]
                                for x in 'p0 p1 p2 p3 p4'.split()]
        assert [u'icemac@example.net',
                u'mail@example.com'] == view.unique_mail_addresses


def test__mailto__MailTo___link__1(mailto_data, browser):
    """The view displays the e-mail adresses of the persons as a link."""
    browser.login('visitor')
    browser.keyword_search('mail-me', apply='E-Mail')
    assert [['<a href="mailto:?bcc=icemac@example.net,mail@example.com">'
             'Click here to open your e-mail client</a>'],
            ['<a href="javascript:history.go(-1)" '
             'class="no-print">Go back</a>']] == [
        browser.etree_to_list(x)
        for x in browser.etree.xpath('//div[@id="mailto"]//a')]
