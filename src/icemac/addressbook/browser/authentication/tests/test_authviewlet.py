def test_authviewlet__FlashedHTTPAuthenticationLogout__logout__1(
        address_book, UserFactory, browser):
    """It renders a message at logout."""
    UserFactory(address_book, u'Hans', u'Tester', u'tester@example.com',
                '1234567890', ['Visitor'])
    browser.formlogin('tester@example.com', '1234567890')
    browser.logout()
    assert (
        ['You have been logged out successfully.',
         'To log-in enter your username and password and submit the form.'] ==
        browser.message)
