import pytest


def assert_masterdata_links(browser, username, link_texts):
    """Assert that the shown links match the expectations."""
    browser.login(username)
    browser.open(browser.MASTER_DATA_URL)
    assert link_texts == browser.etree.xpath(
        '//ul[@class="bullet"]/li/a/span/child::text()')

# There are some master data which can be edited by persons who are
# allowed to. There is a master data overview which shows all parts the
# user can see, this differs between the roles.


def test_masterdata_security__1(address_book, browser):
    """A manager sees all links on the master data page."""
    assert_masterdata_links(
        browser, 'mgr', ['Address book', 'Keywords', 'Users', 'Entities'])


@pytest.mark.parametrize('username', ['editor', 'visitor'])
def test_masterdata_security__2(address_book, browser, username):
    """The editor sees some links on the master data page"""
    assert_masterdata_links(browser, username, ['Keywords', 'Users'])
