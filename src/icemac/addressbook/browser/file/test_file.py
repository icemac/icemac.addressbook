# -*- coding: utf-8 -*-
from StringIO import StringIO
from icemac.addressbook.browser.file.file import cleanup_filename
from icemac.addressbook.file.interfaces import IFile
from zope.testbrowser.browser import LinkNotFoundError
import pytest


def test_file__cleanup_filename__1():
    """cleanup_filename() handles `None` file name."""
    assert '<no name>' == cleanup_filename(None)


def test_file__cleanup_filename__2():
    """cleanup_filename() handles simple file name."""
    assert 'sample.txt' == cleanup_filename('sample.txt')


def test_file__cleanup_filename__3():
    """cleanup_filename() handles Unix file name."""
    assert 'sample.txt' == cleanup_filename('/home/user/sample.txt')


def test_file__cleanup_filename__4():
    """cleanup_filename() handles Windows file name."""
    assert 'sample.txt' == cleanup_filename(r'c:\Users\me\sample.txt')


def test_file__cleanup_filename__5():
    """cleanup_filename() handles UNC file name."""
    assert 'sample.txt' == cleanup_filename(r'\\server\mine\sample.txt')


def test_file__Add__1(address_book, FullPersonFactory, browser, tmpfile):
    """`Add` allows to add a file to a person."""
    FullPersonFactory(address_book, u'Tester')
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getLink('file').click()
    assert browser.FILE_ADD_URL == browser.url
    fh, filename = tmpfile('File contents', '.txt')
    browser.getControl('file').add_file(fh, 'text/plain', filename)
    browser.getControl('Add').click()
    assert '"%s" added.' % filename == browser.message
    assert browser.PERSON_EDIT_URL == browser.url
    # The new file is shown there including a widget displaying the
    # normalized name and mime type:
    assert browser.getControl('file name').value == filename
    assert 'text/plain' == browser.getControl('Mime Type').value
    # But there is no file displayed:
    assert browser.getControl('file', index=1).value is None
    # There is also a download link for the file:
    browser.getLink('Download file').click()
    assert not browser.isHtml
    assert 'text/plain' == browser.headers['content-type']
    assert browser.headers[
        'content-disposition'] == 'attachment; filename=' + filename
    assert '13' == browser.headers['content-length']
    assert 'File contents' == browser.contents


def test_file__Add__2(address_book, FullPersonFactory, browser):
    """`Add` requires a file to be uploaded."""
    FullPersonFactory(address_book, u'Tester')
    browser.login('editor')
    browser.open(browser.FILE_ADD_URL)
    browser.getControl('Add').click()
    assert [] == browser.message
    assert browser.FILE_ADD_URL == browser.url
    assert ['Required input is missing.'] == browser.etree.xpath(
        '/descendant-or-self::ul[@class="errors"]/li/div/text()')


def test_file__Add__3(address_book, FullPersonFactory, browser):
    """`Add` allows to cancel adding."""
    FullPersonFactory(address_book, u'Tester')
    browser.login('editor')
    browser.open(browser.FILE_ADD_URL)
    browser.getControl('Cancel').click()
    assert 'Addition canceled.' == browser.message
    assert browser.PERSON_EDIT_URL == browser.url
    with pytest.raises(LookupError) as err:
        browser.getControl('file')
    assert str(err.value).startswith("label 'file'")


def test_file__Add__4(address_book, FieldFactory, FullPersonFactory, browser):
    """`'Add` displays user defined fields."""
    FieldFactory(address_book, IFile, 'Text', u'mynotes')
    FullPersonFactory(address_book, u'Tester')
    browser.login('editor')
    browser.open(browser.FILE_ADD_URL)
    browser.getControl('file').add_file(
        StringIO('Dear Tester, CU.'), 'text/plain', 'letter.txt')
    browser.getControl('mynotes').value = 'first letter'
    browser.getControl('Add').click()
    assert '"letter.txt" added.' == browser.message
    assert browser.PERSON_EDIT_URL == browser.url
    # The entered values got saved:
    assert 'text/plain' == browser.getControl('Mime Type').value
    assert 'letter.txt' == browser.getControl('name', index=2).value
    assert 'first letter' == browser.getControl('mynotes').value


def test_file__Add__5(address_book, FullPersonFactory, browser):
    """It cannot be accessed by a visitor."""
    FullPersonFactory(address_book, u'Tester')
    browser.login('visitor')
    browser.open(browser.PERSON_EDIT_URL)
    # There is no add link
    with pytest.raises(LinkNotFoundError):
        browser.getLink('file').click()
    # Direct access to the URL is forbidden:
    browser.assert_forbidden(browser.FILE_ADD_URL)


def test_file__Add__5_2(address_book, FullPersonFactory, browser):
    """It cannot be accessed by an archivist."""
    FullPersonFactory(address_book, u'Tester')
    browser.login('archivist')
    browser.assert_forbidden(browser.FILE_ADD_URL)


def test_file__Add__6(address_book, FullPersonFactory, browser, tmpfile):
    """It can handle larger files.

    Small files are not written to disk but handled via a StringIO.

    """
    FullPersonFactory(address_book, u'Tester')
    browser.login('editor')
    browser.open(browser.FILE_ADD_URL)
    fh, filename = tmpfile('File contents ' * 1024, '.txt')
    browser.getControl('file').add_file(fh, 'text/plain', filename)
    browser.getControl('Add').click()
    assert '"%s" added.' % filename == browser.message
    # A larger file can be downloaded successfully.
    browser.getLink('Download file').click()
    assert '14336' == browser.headers['content-length']
    assert browser.contents.startswith('File contents File contents')


def test_file__Add__Edit__Download__1(
        address_book, FullPersonFactory, FileFactory, browser, tmpfile):
    """It allows to upload, change and download more than one file."""
    # Upload
    FileFactory(FullPersonFactory(address_book, u'Test'), u'my-file.txt',
                data='boring text')
    browser.login('editor')
    browser.open(browser.FILE_ADD_URL)
    browser.getControl('file').add_file(
        StringIO('2nd file'), 'text/plain', '2nd.txt')
    browser.getControl('Add').click()
    assert '"2nd.txt" added.' == browser.message
    assert browser.PERSON_EDIT_URL == browser.url
    assert browser.getControl('name', index=3).value == '2nd.txt'
    assert 'text/plain' == browser.getControl('Mime Type', index=1).value
    assert browser.getControl('file', index=1).value is None
    # Download
    browser.getLink('Download file', index=1).click()
    assert 'text/plain' == browser.headers['content-type']
    assert (browser.headers['content-disposition'] ==
            'attachment; filename=2nd.txt')
    assert '8' == browser.headers['content-length']
    assert '2nd file' == browser.contents
    # Change
    browser.open(browser.PERSON_EDIT_URL)
    fh, filename = tmpfile('3rd try', '.txt')
    browser.getControl('file', index=3).add_file(fh, 'text/enriched', filename)
    browser.getControl('Save').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    # Assert changes
    browser.open(browser.PERSON_EDIT_URL)
    assert browser.getControl('file name', index=1).value == filename
    assert 'text/enriched' == browser.getControl('Mime Type', index=1).value
    # Download changed file
    browser.getLink('Download file', index=1).click()
    assert 'text/enriched' == browser.headers['content-type']
    assert (browser.headers['content-disposition'] ==
            'attachment; filename=' + filename)
    assert '3rd try' == browser.contents


def test_file__DeleteFileForm__1(
        address_book, FullPersonFactory, FileFactory, browser):
    """A File can be deleted using the ``Delete single entry`` button."""
    person = FullPersonFactory(address_book, u'Test')
    FileFactory(person, u'my-file.txt', data='boring text')
    FileFactory(person, u'data.dat', data='<XML :/>')
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getControl('Delete single entry').click()
    assert browser.PERSON_DELETE_ENTRY_URL == browser.url
    assert ['postal address -- Germany',
            'phone number -- none',
            'e-mail address -- none',
            'home page address -- none',
            'file -- my-file.txt',
            'file -- data.dat'] == browser.getControl('Entries').displayOptions
    browser.getControl('Entries').getControl(
        'file -- my-file.txt').selected = True
    browser.getControl('Delete entry').click()
    # Before the entry gets deleted, an `are you sure` formular is presented
    # where the user can choose to cancel.
    assert browser.FILE_DELETE_URL == browser.url
    browser.getControl('Yes').click()
    assert '"my-file.txt" deleted.' == browser.message
    assert browser.PERSON_EDIT_URL == browser.url
    # The deleted file is no longer displayed (there is now only one file):
    with pytest.raises(LookupError) as err:
        browser.getControl('file name', index=1)
    assert str(err.value).startswith(
        "label 'file name'\nIndex 1 out of range, available choices are 0...0")


@pytest.mark.parametrize('loginname', ['visitor', 'archivist'])
def test_file__DeleteFileForm__2(
        address_book, FullPersonFactory, FileFactory, browser, loginname):
    """`DeleteFileForm` cannot be accessed by some roles."""
    FileFactory(FullPersonFactory(address_book, u'Test'), u'my-file.txt',
                data='boring text')
    browser.login(loginname)
    browser.assert_forbidden(browser.FILE_DELETE_URL)
