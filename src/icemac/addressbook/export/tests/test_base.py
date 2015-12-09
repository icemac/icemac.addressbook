import icemac.addressbook.export.base
import icemac.addressbook.export.interfaces
import pytest
import zope.interface.verify


def test_base__BaseExport__1():
    """`BaseExport` conforms to `IExporter`."""
    assert zope.interface.verify.verifyObject(
        icemac.addressbook.export.interfaces.IExporter,
        icemac.addressbook.export.base.BaseExporter([], None))


def test_base__BaseExport__export__1():
    """`export` is not implemented."""
    # Test is only here to get better test coverage.
    exporter = icemac.addressbook.export.base.BaseExporter(None)
    with pytest.raises(NotImplementedError):
        exporter.export()
