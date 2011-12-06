import icemac.addressbook.testing
import unittest2 as unittest
import mock
import plone.testing


class MailToLayer(plone.testing.Layer):

    defaultBases = [icemac.addressbook.testing.WSGI_TEST_BROWSER_LAYER]

    def setUp(self):
        from icemac.addressbook.testing import (
            create_person, create_full_person, create_email_address,
            createZODBConnection, setUpStackedDemoStorage, setUpAddressBook)
        import transaction
        setUpStackedDemoStorage(self, 'SearchLayer')
        ab = setUpAddressBook(self)
        setupZODBConn, rootObj, rootFolder = createZODBConnection(
            self['zodbDB'])

        kw = set([icemac.addressbook.testing.create_keyword(ab, u'mail-me')])
        # No EMailAddress object
        self['p0'] = create_person(ab, ab, u'No Mail', keywords=kw)
        self['p1'] = create_person(ab, ab, u'Mail', keywords=kw)
        create_email_address(ab, self['p1'], email=u'icemac@example.net')
        self['p2'] = create_person(ab, ab, u'Mail Too', keywords=kw)
        create_email_address(ab, self['p2'], email=u'mail@example.com')
        self['p3'] = create_person(ab, ab, u'Double Mail', keywords=kw)
        # Dulicate email address
        create_email_address(ab, self['p3'], email=u'mail@example.com')
        self['p4'] = create_full_person(ab, ab, u'Other Mail', keywords=kw)
        # default email address is None
        create_email_address(
            ab, self['p4'], email=u'other@example.com', set_as_default=False)
        transaction.commit()
        setupZODBConn.close()

    def tearDown(self):
        del self['p0']
        del self['p1']
        del self['p2']
        del self['p3']
        del self['p4']
        icemac.addressbook.testing.tearDownStackedDemoStorage(self)

MAILTO_LAYER = MailToLayer()


class MailToTest(unittest.TestCase):
    """Testing .mailto.MailTo."""

    layer = MAILTO_LAYER

    def get_view(self):
        from .mailto import MailTo
        view = MailTo()
        view.request = mock.Mock()
        return view

    @mock.patch('icemac.addressbook.browser.base.get_session')
    def test_persons_returns_persons_for_ids_in_session(self, session):
        from icemac.addressbook.testing import (
            create_person, create_full_person, create_email_address)
        persons = [self.layer[x] for x in 'p1 p2'.split()]
        session.return_value = dict(person_ids=[x.__name__ for x in persons])
        self.assertEqual(persons, list(self.get_view().get_persons()))

    get_persons = ('icemac.addressbook.browser.search.result.handler.mailto.'
                   'mailto.MailTo.get_persons')

    @mock.patch(get_persons)
    def test_unique_mail_addresses_returns_sorted_unique_email_addresses(
            self, get_persons):
        get_persons.return_value = [
            self.layer[x] for x in 'p0 p1 p2 p3 p4'.split()]

        self.assertEqual([u'icemac@example.net', u'mail@example.com'],
                         self.get_view().unique_mail_addresses)

    def test_view_displays_mail_adresses_of_selected_persons_as_link(self):
        from icemac.addressbook.browser.testing import (
            search_for_persons_with_keyword_search_using_browser)
        browser = search_for_persons_with_keyword_search_using_browser(
            'mail-me', 'visitor')
        browser.handleErrors = False
        browser.getControl('Apply on selected persons').displayValue = [
            'E-Mail']
        browser.getControl(name='form.buttons.apply').click()
        file('response.html', 'w').write(browser.contents)
        self.assertEqual(
            ['<div id="mailto">',
             '<h2>Send an e-mail</h2>',
             '<a href="mailto:?bcc=icemac@example.net,mail@example.com">'
             'Click here to open your e-mail client</a>',
             '</div>'],
            browser.etree_to_list(
                browser.etree.xpath('//div[@id="mailto"]')[0]))
