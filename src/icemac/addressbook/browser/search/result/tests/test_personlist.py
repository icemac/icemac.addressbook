import pytest


@pytest.mark.webdriver
def test_personlist__PersonTable__1(search_data, webdriver):
    """The `checkall` checkbox deselects and reselects all persons."""
    s = webdriver.login('visitor')
    s.open('/ab/@@multi_keyword.html')
    s.addSelection('id=form-widgets-keywords', 'label=family')
    s.clickAndWait('id=form-buttons-search')
    # There are two lines of search results:
    s.assertCssCount('name=persons:list', 2)
    # Checked by default:
    s.assertChecked('name=persons:list')
    # Deselect all with a single click:
    s.click('css=input.checkall')
    s.assertNotChecked('name=persons:list')
    # Select again:
    s.click('css=input.checkall')
    s.assertChecked('name=persons:list')


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
