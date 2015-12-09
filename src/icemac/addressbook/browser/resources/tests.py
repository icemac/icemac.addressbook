def test_resources__1(address_book, browser):
    """Image resources can be delivered to the browser."""
    browser.open('http://localhost/++resource++img/Symbol-Information.png')
    assert '200 Ok' == browser.headers['status']
