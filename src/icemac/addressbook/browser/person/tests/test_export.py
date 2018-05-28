def test_export__ExportList__1(search_data, browser):
    """..export.ExportList() renders an advice if there are no exporters.

    The actual exporters are tested in their modules.

    """
    browser.login('visitor')
    browser.open(browser.PERSONS_LIST_URL)
    browser.getLink('Hohmuth').click()
    browser.getControl('Export').click()
    assert ('You did not enter enough data of the person, '
            'so no export is possible.' in browser.contents)
