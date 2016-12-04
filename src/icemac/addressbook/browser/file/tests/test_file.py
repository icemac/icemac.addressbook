# -*- coding: utf-8 -*-
from StringIO import StringIO
from icemac.addressbook.browser.file.file import cleanup_filename
from icemac.addressbook.file.interfaces import IFile
from mechanize import HTTPError, LinkNotFoundError
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
    """`Add` cannot be accessed by a visitor."""
    FullPersonFactory(address_book, u'Tester')
    browser.login('visitor')
    browser.open(browser.PERSON_EDIT_URL)
    # There is no add link
    with pytest.raises(LinkNotFoundError) as err:
        browser.getLink('file').click()
    # Direct access to the URL is forbidden:
    with pytest.raises(HTTPError) as err:
        browser.open(browser.FILE_ADD_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)


def test_file__Edit__1(address_book, FullPersonFactory, FileFactory, browser):
    """`Edit` allows to change the name and mimetype of the file."""
    FileFactory(FullPersonFactory(address_book, u'Test'), u'my-file.txt',
                data='boring text')
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    browser.getControl('name', index=2).value = 'my nice file.txt'
    browser.getControl('Mime Type').value = 'text/example'
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url


def test_file__Edit__2(
        address_book, FullPersonFactory, FileFactory, browser, tmpfile):
    """`Edit` allows to upload a new file.

    This changes the name and the mime type if necessary. When the browser does
    not know the mime type and sends ``application/octet-stream``, the mime
    type is guessed using the file extension and file contents.

    """
    FileFactory(FullPersonFactory(address_book, u'Test'), u'my-file.txt',
                data='boring text')
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    fh, filename = tmpfile('special data, blah', '.js')
    browser.getControl('file', index=1).add_file(
        fh, 'application/octet-stream', filename)
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    # The downloaded file behaves accordingly:
    browser.open(browser.PERSON_EDIT_URL)
    assert browser.getControl('file name').value == filename
    assert 'application/javascript' == browser.getControl('Mime Type').value


def test_file__Edit__3(
        address_book, FullPersonFactory, FileFactory, browser, tmpfile):
    """`Edit` correctly handles a missing mime-type.

    The mime type is optional, if the browser of the client does not send
    a content type and zope.mimetype can't determine the mime type from
    the filename or file content, it is set to ``application/octet-stream``.

    """
    FileFactory(FullPersonFactory(address_book, u'Test'), u'my-file.txt',
                data='boring text')
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    fh, filename = tmpfile('Ä, no content type, huh', '')
    browser.getControl('file', index=1).add_file(fh, '', filename)
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    browser.open(browser.PERSON_EDIT_URL)
    assert 'application/octet-stream' == browser.getControl('Mime Type').value


def test_file__Edit__4(
        address_book, FieldFactory, FullPersonFactory, FileFactory, browser):
    """The data in the user defined field on a file can be edited."""
    field_name = FieldFactory(address_book, IFile, 'Text', u'mynotes').__name__
    person = FullPersonFactory(address_book, u'Tester')
    FileFactory(person, **{'filename': u'foo.txt', field_name: 'first letter'})
    browser.login('editor')
    browser.open(browser.PERSON_EDIT_URL)
    assert 'first letter' == browser.getControl('mynotes').value
    browser.getControl('mynotes').value = 'second letter'
    browser.getControl('Apply').click()
    assert 'Data successfully updated.' == browser.message
    assert browser.PERSONS_LIST_URL == browser.url
    browser.getLink('Tester').click()
    assert 'second letter' == browser.getControl('mynotes').value


def test_file__Edit__5(address_book, FullPersonFactory, FileFactory, browser):
    """A visitor is not able to edit a file."""
    FileFactory(FullPersonFactory(address_book, u'Test'), u'my-file.txt',
                data='boring text')
    browser.login('visitor')
    browser.open(browser.PERSON_EDIT_URL)
    # There are neither any input widgets nor a delete button:
    assert ['form.buttons.apply',
            'form.buttons.cancel',
            'form.buttons.export'] == browser.all_control_names


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
    browser.getControl('Apply').click()
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


def test_file__DeleteFileForm__2(
        address_book, FullPersonFactory, FileFactory, browser):
    """`DeleteFileForm` cannot be accessed by a visitor."""
    FileFactory(FullPersonFactory(address_book, u'Test'), u'my-file.txt',
                data='boring text')
    browser.login('visitor')
    with pytest.raises(HTTPError) as err:
        browser.open(browser.FILE_DELETE_URL)
    assert 'HTTP Error 403: Forbidden' == str(err.value)
