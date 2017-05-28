from icemac.addressbook.namechooser.interfaces import IDontReuseNames
from icemac.addressbook.namechooser.interfaces import INameSuffix
from icemac.addressbook.namechooser.namechooser import DontReuseNames
from icemac.addressbook.namechooser.namechooser import NameSuffix
from zope.interface.verify import verifyObject
import mock
import pytest
import six
import zope.annotation.interfaces
import zope.container.sample
import zope.interface


@pytest.yield_fixture(scope='function')
def NameChooserFactory(zcmlS):
    """Get a function to create a name chooser."""
    patchers = []

    def create_name_chooser(name_suffix, patchers=patchers):
        """Create a name chooser with `name_suffix` as current suffix value."""
        nc = DontReuseNames(mock.MagicMock())
        patcher = mock.patch.object(
            DontReuseNames, 'name_suffix', new_callable=mock.PropertyMock)
        name_suffix_mock = patcher.start()
        name_suffix_mock.return_value = name_suffix
        patchers.append(patcher)  # handover the patcher to tear down
        return nc
    yield create_name_chooser
    for patcher in patchers:
        patcher.stop()


def test_namechooser__NameSuffix__1():
    """`NameSuffix` conforms to INameChooser."""
    assert verifyObject(INameSuffix, NameSuffix())


def test_namechooser__NameSuffix__2():
    """`NameSuffix` starts with a value of zero."""
    assert u'0' == six.text_type(NameSuffix())


def test_namechooser__NameSuffix__3():
    """`NameSuffix` sums up."""
    name_suffix = NameSuffix()
    name_suffix += 3
    name_suffix += 2
    assert u'5' == six.text_type(name_suffix)


def test_namechooser__DontReuseNames__chooseName__1(NameChooserFactory):
    """`chooseName()` includes a suffix even for the first name."""
    namechooser = NameChooserFactory(0)
    assert u'foo-1' == namechooser.chooseName('foo', object())


def test_namechooser__DontReuseNames__chooseName__2(NameChooserFactory):
    """`chooseName()` counts the suffix up."""
    namechooser = NameChooserFactory(1)
    assert u'foo-2' == namechooser.chooseName('foo', object())


def test_namechooser__DontReuseNames__chooseName__3(NameChooserFactory):
    """`chooseName()` ignores the name prefix when counting."""
    namechooser = NameChooserFactory(1)
    assert u'bar-2' == namechooser.chooseName('bar', object())


def test_namechooser__DontReuseNames__chooseName__4(NameChooserFactory):
    """`chooseName()` puts the suffix before the extension in the name."""
    namechooser = NameChooserFactory(6)
    assert u'baz-7.txt' == namechooser.chooseName('baz.txt', object())


def test_namechooser__DontReuseNames__chooseName__5(NameChooserFactory):
    """`chooseName()` strips leading + signs from name."""
    namechooser = NameChooserFactory(5)
    assert u'b+z+-6' == namechooser.chooseName('+++b+z+', object())


def test_namechooser__DontReuseNames__chooseName__6(NameChooserFactory):
    """`chooseName()` strips leading @ signs from name."""
    namechooser = NameChooserFactory(5)
    assert u'b@z@-6' == namechooser.chooseName('@@b@z@', object())


def test_namechooser__DontReuseNames__chooseName__7(NameChooserFactory):
    """`chooseName()` replaces slashes with minus signs."""
    namechooser = NameChooserFactory(5)
    assert u'-b-a-z--6' == namechooser.chooseName('/b/a/z/', object())


def test_namechooser__DontReuseNames__chooseName__8(NameChooserFactory):
    """`chooseName()` uses the class name if name is empty after stripping."""
    namechooser = NameChooserFactory(2)
    assert u'object-3' == namechooser.chooseName('+', object())


def test_namechooser__DontReuseNames__chooseName__9(NameChooserFactory):
    """`chooseName()` omits a name alredy used in the container."""
    nc = NameChooserFactory(2)
    with mock.patch.object(nc, 'name_in_use', side_effect=[True, False]):
        assert u'foo-4' == nc.chooseName('foo', object())


def test_namechooser__DontReuseNames__1(zcmlS):
    """`DontReuseNames` stores its data on the container."""
    container = zope.container.sample.SampleContainer()
    zope.interface.alsoProvides(container, IDontReuseNames)
    zope.interface.alsoProvides(
        container, zope.annotation.interfaces.IAttributeAnnotatable)
    nc = zope.container.interfaces.INameChooser(container)
    assert isinstance(nc, DontReuseNames)
    assert u'foo-1' == nc.chooseName('foo', object())
    nc2 = zope.container.interfaces.INameChooser(container)
    assert u'foo-2' == nc2.chooseName('foo', object())
