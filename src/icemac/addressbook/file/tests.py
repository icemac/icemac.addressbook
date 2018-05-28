from icemac.addressbook.file.file import File
import icemac.addressbook.file.interfaces
import transaction
import zope.interface.verify


def test_file__File__1():
    """`File` conforms to `IFile`."""
    assert zope.interface.verify.verifyObject(
        icemac.addressbook.file.interfaces.IFile, File())


def test_file__File__size__1():
    """An empty file has the length of zero."""
    assert 0 == File().size


def test_file__File__size__2():
    """`size` counts the length of the file.."""
    assert 10 == File('1234567\n90').size


def test_file__File__open__1():
    """`open()` allows to read and write the underlying file."""
    f = File()
    fd = f.open('w')
    fd.write('qwertz.123')
    fd.close()
    try:
        fd = f.open('r')
        assert 'qwertz.123' == fd.read()
    finally:
        fd.close()


def test_file__File__data__1():
    """`data` always returns '' to trick z3c.form."""
    f = File()
    f.data = 'data'
    assert '' == f.data


def test_file__File__openDetached__1(empty_zodb):
    """`openDetached` returns file data disconnected from db connection."""
    # need to assign to tree, so commit works
    empty_zodb.rootFolder['f'] = f = File('data\n\nfoobar')
    # commit as openDetached expects a committed blob
    transaction.commit()
    try:
        fd = f.openDetached()
        assert 'data\n\nfoobar' == fd.read()
    finally:
        fd.close()


def test_file__File__replace__1(empty_zodb, tmpdir):
    """`replace` allows to replace a file by another using its filename."""
    # need to assign to tree, so commit works
    empty_zodb.rootFolder['f2'] = f = File('1234')
    fdw = tmpdir.join('other.file')
    fdw.write('6789\n0123')
    filename = str(fdw)
    f.replace(filename)
    transaction.commit()
    try:
        fdr = f.openDetached()
        assert '6789\n0123' == fdr.read()
    finally:
        fdr.close()
