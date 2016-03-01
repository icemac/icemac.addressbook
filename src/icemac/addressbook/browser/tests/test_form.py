from ..form import zope_i18n_pattern_to_jquery_pattern
from datetime import datetime
from icemac.addressbook.interfaces import IKeyword
from mock import patch, Mock
from pytz import utc, timezone
import gocept.testing.mock
import icemac.addressbook.browser.form
import pytest
import zope.publisher.browser


@pytest.fixture(scope='function')
def DatetimeDataConverter(mockTimeZone):
    """Set up a `DatetimeDataConverter` object for tests."""
    widget = Mock()
    widget.request = zope.publisher.browser.TestRequest()
    field = Mock()
    field.missing_value = None
    return icemac.addressbook.browser.form.DatetimeDataConverter(field, widget)


@pytest.yield_fixture(scope='module')
def mockTimeZone():
    """Mock the timezone set in preferences to 'Etc/GMT-4'."""
    time_zone = ('icemac.addressbook.browser.form.'
                 'DatetimeDataConverter.time_zone')
    with patch(time_zone, gocept.testing.mock.Property()) as time_zone:
        time_zone.return_value = timezone('Etc/GMT-4')
        yield


def test_form__DatetimeDataConverter__toWidgetValue__1(DatetimeDataConverter):
    """`toWidgetValue` renders datetime with timezone localized."""
    assert u'13/02/01 21:20' == DatetimeDataConverter.toWidgetValue(
        datetime(2013, 2, 1, 17, 20, tzinfo=utc))


def test_form__DatetimeDataConverter__toWidgetValue__2(DatetimeDataConverter):
    """`toWidgetValue` renders naive datetime unchanged."""
    assert u'13/02/01 17:20' == DatetimeDataConverter.toWidgetValue(
        datetime(2013, 2, 1, 17, 20))


def test_form__DatetimeDataConverter__toWidgetValue__3(DatetimeDataConverter):
    """`toWidgetValue` renders `missing_value` as empty string."""
    assert u'' == DatetimeDataConverter.toWidgetValue(None)


def test_form__DatetimeDataConverter__toFieldValue__1(DatetimeDataConverter):
    """`toFieldValue` adds tzinfo."""
    assert (datetime(2013, 2, 1, 21, 20, tzinfo=timezone('Etc/GMT-4')) ==
            DatetimeDataConverter.toFieldValue(u'13/02/01 21:20'))


def test_form__DatetimeDataConverter__toFieldValue__2(DatetimeDataConverter):
    """`toFieldValue` leaves an empty value alone."""
    assert None is DatetimeDataConverter.toFieldValue(u'')


def test_form__zope_i18n_pattern_to_jquery_pattern__1():
    """Function converts German datetime format correctly."""
    assert ('dd.mm.y HH:mm' ==
            zope_i18n_pattern_to_jquery_pattern('datetime', 'dd.MM.yy HH:mm'))


def test_form__zope_i18n_pattern_to_jquery_pattern__2():
    """Function converts American datetime format correctly."""
    assert ('m/d/y hh:mm TT' ==
            zope_i18n_pattern_to_jquery_pattern('datetime', 'M/d/yy h:mm a'))


def test_form__zope_i18n_pattern_to_jquery_pattern__3():
    """Function converts American time format correctly."""
    assert ('h:mm TT' == zope_i18n_pattern_to_jquery_pattern('time', 'h:mm a'))


@pytest.mark.parametrize('datatype', ['Datetime', 'Time'])
def test_form__Widget__1(
        address_book, FieldFactory, KeywordFactory, datatype, webdriver):
    """`DatetimeWidget` renders a JavaScript calendar."""
    FieldFactory(address_book, IKeyword, datatype, u'my-field')
    kw = KeywordFactory(address_book, u'foobar')
    s = webdriver.login('editor')
    s.open('/ab/++attribute++keywords/%s' % kw.__name__)
    # Activate the datetime field which opens the JavaScript calendar
    s.click('id=form-widgets-Field-1')
    # Click the `now` button:
    s.click("//button[@type='button']")
    # And the `done` button:
    s.click("xpath=(//button[@type='button'])[2]")
    # Save the form:
    s.clickAndWait("id=form-buttons-apply")
    # Successful apply leads back to keyword overview:
    assert s.getLocation().endswith('/ab/++attribute++keywords')


def test_form__DateWidget__1(address_book, webdriver):
    """`DateWidget` renders a JavaScript calendar."""
    s = webdriver.login('editor')
    s.open('/ab/@@addPerson.html')
    # Activate the date field which opens the JavaScript calendar
    s.click('id=IcemacAddressbookPersonPerson-widgets-'
            'IcemacAddressbookPersonPerson-birth_date')
    # Click the first of the first month:
    s.click("link=1")
    # Fill in required fiels:
    s.type('id=IcemacAddressbookPersonPerson-widgets-'
           'IcemacAddressbookPersonPerson-last_name', 'Tester')
    # Save the form:
    s.clickAndWait("id=form-buttons-add")
    # Successful apply leads back to keyword overview
    assert s.getLocation().endswith('/ab/@@person-list.html')
