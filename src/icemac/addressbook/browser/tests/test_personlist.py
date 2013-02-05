from mock import Mock, patch
import unittest


class DateTimeColumn_getSortKey_Tests(unittest.TestCase):
    """Testing ..personlist.DateTimeColumn.getSortKey."""

    def callMUT(self, value):
        from ..personlist import DateTimeColumn
        col = DateTimeColumn(Mock(), Mock(), Mock())
        getRawValue = ('icemac.addressbook.browser.personlist.'
                       'DateTimeColumn.getRawValue')
        with patch(getRawValue) as getRawValue:
            getRawValue.return_value = value
            return col.getSortKey(Mock())

    def test_getSortKey_returns_value_which_is_always_compareable(self):
        from datetime import datetime
        from pytz import timezone
        # We use the isoformat as sort key, so comparison does not break if
        # we nix timezone naive and timezone aware datetimes. And yes, we
        # know that this might produce some glitches in the sort order but
        # it is better than an HTTP-500 and better than trying to guess
        # timezone information.
        self.assertEqual('2012-02-02T21:57:00',
                         self.callMUT(datetime(2012, 2, 2, 21, 57)))
        self.assertEqual('2012-02-02T21:57:00+04:00',
                         self.callMUT(datetime(2012, 2, 2, 21, 57,
                                               tzinfo=timezone('Etc/GMT-4'))))
        self.assertEqual('9999-12-31T23:59:59', self.callMUT(None))
