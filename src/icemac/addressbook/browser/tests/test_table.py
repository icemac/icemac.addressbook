from datetime import datetime
from mock import Mock, patch
from pytz import timezone
import icemac.addressbook.browser.table


def getSortKey(value):
    """Helper function to call the `getSortKey()` method of `DateTimeColumn.`.

    Assuming `value` is the raw value.
    """
    col = icemac.addressbook.browser.table.DateTimeColumn(
        Mock(), Mock(), Mock())
    getRawValue = (
        'icemac.addressbook.browser.table.DateTimeColumn.getRawValue')
    with patch(getRawValue) as getRawValue:
        getRawValue.return_value = value
        return col.getSortKey(Mock())


def test_table__DateTimeColumn__getSortKey__1():
    """`getSortKey` returns isoformat for naive datetime."""
    assert ('2012-02-02T21:57:00' ==
            getSortKey(datetime(2012, 2, 2, 21, 57)))


def test_table__DateTimeColumn__getSortKey__2():
    """`getSortKey` returns isoformat for timezone aware datetime."""
    assert ('2012-02-02T21:57:00+04:00' ==
            getSortKey(
                datetime(2012, 2, 2, 21, 57, tzinfo=timezone('Etc/GMT-4'))))


def test_table__DateTimeColumn__getSortKey__3():
    """`getSortKey` returns isoformat for `None` value to sort it down."""
    assert '9999-12-31T23:59:59' == getSortKey(None)
