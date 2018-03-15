def test_download__Download__1(
        address_book, FullPersonFactory, FileFactory, browser):
    """`Download` uses name and mimetype of the file.

    Spaces in the file name are replaced by underscores:

    """
    FileFactory(FullPersonFactory(address_book, u'Test'), u'my nice file.txt',
                data='boring text', mimeType='text/example')
    browser.login('visitor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getLink('Download file').click()
    assert browser.FILE_DOWNLOAD_URL == browser.url
    assert 'text/example' == browser.headers['content-type']
    assert 'attachment; filename=my_nice_file.txt' == browser.headers[
        'content-disposition']
    assert 'boring text' == browser.contents


def test_download__Download__2(
        address_book, FullPersonFactory, FileFactory, browser):
    """`Download` renders a missing mimetype as ``application/octet-stream``.

    Spaces in the file name are replaced by underscores:

    """
    FileFactory(FullPersonFactory(address_book, u'Test'), u'my nice file.txt',
                mimeType=None)
    browser.login('visitor')
    browser.open(browser.FILE_DOWNLOAD_URL)
    assert 'application/octet-stream' == browser.headers['content-type']


def test_download__Download__3(
        address_book, FullPersonFactory, FileFactory, browser):
    """A visitor can download a file-"""
    FileFactory(FullPersonFactory(address_book, u'Test'), u'v.txt',
                data='visiting', mimeType='text/plain')
    browser.login('visitor')
    browser.open(browser.FILE_DOWNLOAD_URL)
    assert 'text/plain' == browser.headers['content-type']
    assert (browser.headers['content-disposition'] ==
            'attachment; filename=v.txt')
    assert 'visiting' == browser.contents
