from icemac.addressbook.testing import WebdriverPageObjectBase, Webdriver
import pytest


class POKeywordSearch(WebdriverPageObjectBase):
    """Webdriver page object for the keyword search page."""

    paths = [
        'SEARCH_BY_KEYWORD_URL',
    ]

    def search(self, keyword):
        self._selenium.addSelection(
            'id=form-widgets-keywords', 'label={}'.format(keyword))
        self._selenium.click('id=form-buttons-search')

    @property
    def num_results(self):
        return self._selenium.getCssCount('name=persons:list')

    @property
    def is_checked(self):
        return self._selenium.isChecked('name=persons:list')

    def hit_checkall(self):
        self._selenium.click('css=input.checkall')


Webdriver.attach(POKeywordSearch, 'keyword_search')


@pytest.mark.webdriver
def test_personlist__PersonTable__1_webdriver(search_data, webdriver):
    """The `checkall` checkbox deselects and reselects all persons."""
    keyword_search = webdriver.keyword_search
    webdriver.login('visitor', keyword_search.SEARCH_BY_KEYWORD_URL)
    keyword_search.search('family')
    # There are two lines of search results:
    assert 2 == keyword_search.num_results
    # The results are checked by default:
    assert keyword_search.is_checked
    keyword_search.hit_checkall()
    assert not keyword_search.is_checked
    # Select again:
    keyword_search.hit_checkall()
    assert keyword_search.is_checked


def test_personlist__ExportForm__1(address_book, browser):
    """The submit button of `ExportForm`' is not shown before searching."""
    browser.login('visitor')
    browser.open(browser.SEARCH_BY_KEYWORD_URL)
    assert [['form.buttons.search']] == browser.submit_control_names_all_forms


def test_personlist__ExportForm__2(address_book, KeywordFactory, browser):
    """The submit button of `ExportForm`' is not shown if nothing found."""
    KeywordFactory(address_book, u'example')
    browser.login('visitor')
    browser.keyword_search('example')
    assert [['form.buttons.search']] == browser.submit_control_names_all_forms


def test_personlist__ExportForm__3(search_data, browser):
    """The submit button of `ExportForm`' is shown if something found."""
    browser.login('visitor')
    browser.keyword_search('church')
    assert ([['form.buttons.search'], ['form.buttons.apply']] ==
            browser.submit_control_names_all_forms)


def test_personlist__ExportForm__4(search_data, browser):
    """It does not break if no handler is selected."""
    browser.login('visitor')
    browser.keyword_search('church')
    browser.getControl('Apply on selected persons').displayValue = []
    browser.getControl(name='form.buttons.apply').click()
    assert '200 Ok' == browser.headers['status']
