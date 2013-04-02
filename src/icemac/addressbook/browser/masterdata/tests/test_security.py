import icemac.addressbook.testing


class MasterdataSecurityTests(icemac.addressbook.testing.BrowserTestCase):
    """Security testing ..masterdata."""

    # There are some masterdata which can be edited by persons who are
    # allowed to. There is a master data overview which shows all parts the
    # user can see, this differs between the roles.

    def assert_masterdata_links(self, username, link_texts):
        browser = self.get_browser(username)
        browser.open('http://localhost/ab/@@masterdata.html')
        self.assertEqual(
            link_texts, browser.etree.xpath(
                '//ul[@class="bullet"]/li/a/span/child::text()'))

    def test_manager_sees_all_links_in_masterdata(self):
        self.assert_masterdata_links(
            'mgr', ['Address book', 'Keywords', 'Users', 'Entities'])

    def test_editor_sees_some_links_in_masterdata(self):
        self.assert_masterdata_links('editor', ['Keywords', 'Users'])

    def test_visitor_sees_some_links_in_masterdata(self):
        self.assert_masterdata_links('visitor', ['Keywords', 'Users'])
