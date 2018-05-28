import pytest


@pytest.mark.parametrize("lang, filename", (
    ('de', 'de.js'),
    ('de-DE', 'de.js'),
    ('de-AT', 'de.js'),
    ('en-US', 'en.js'),
    ('is', 'is.js'),
    ('C', 'en.js'),  # unknown lang defaults to en.js
))
def test_resouce__DefaultResources__1(address_book, browser, lang, filename):
    """It requires the select2 i18n files corresponding to the browser lang."""
    browser.lang(lang)
    browser.login('editor')
    browser.handleErrors = False
    browser.open(browser.PERSON_ADD_URL)
    assert '/js/i18n/{}">'.format(filename) in browser.contents
