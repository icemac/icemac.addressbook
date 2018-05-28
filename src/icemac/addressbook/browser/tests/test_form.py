from ..form import zope_i18n_pattern_to_jquery_pattern, FieldDescriptionAsHint
from datetime import datetime
from icemac.addressbook.interfaces import IKeyword
from icemac.addressbook.testing import WebdriverPageObjectBase, Webdriver
from mock import patch, Mock
from pytz import utc, timezone
import gocept.testing.mock
import icemac.addressbook.browser.form
import pytest
import six
import zope.i18nmessageid
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


@pytest.fixture('function')
def po_datetime_webdriver():
    """Webdriver page object for the datetime widget."""
    class PODatetime(WebdriverPageObjectBase):
        paths = [
            'KEYWORD_EDIT_URL',
            'KEYWORDS_LIST_URL'
        ]

        def datetime_now(self):
            s = self._selenium
            # Activate the datetime field which opens the JavaScript calendar
            s.click('id=form-widgets-Field-1')
            # Click the `now` button:
            s.click("//button[@type='button']")
            # And the `done` button:
            s.click("xpath=(//button[@type='button'])[2]")

        def save(self):
            self._selenium.click("id=form-buttons-apply")

    Webdriver.attach(PODatetime, 'dt')
    yield
    Webdriver.detach(PODatetime, 'dt')


@pytest.mark.flaky(reruns=3)
@pytest.mark.webdriver
@pytest.mark.parametrize('datatype', ['Datetime', 'Time'])
def test_form__Widget__1_webdriver(address_book, FieldFactory, KeywordFactory, datatype, po_datetime_webdriver, webdriver):  # noqa
    """`DatetimeWidget` renders a JavaScript calendar."""
    FieldFactory(address_book, IKeyword, datatype, u'my-field')
    KeywordFactory(address_book, u'foobar')
    dt = webdriver.dt
    webdriver.login('editor', dt.KEYWORD_EDIT_URL)
    webdriver.windowMaximize()
    dt.datetime_now()
    dt.save()
    # Successful apply leads back to keyword overview:
    assert dt.KEYWORDS_LIST_URL == webdriver.path


def test_form__TimeWidget__2(
        address_book, FieldFactory, KeywordFactory, browser):
    """It renders a JavaScript calendar. (test for coverage)"""
    FieldFactory(address_book, IKeyword, 'Time', u'my-field')
    KeywordFactory(address_book, u'foobar')
    browser.login('editor')
    browser.open(browser.KEYWORD_EDIT_URL)
    assert '"timeFormat": "HH:mm",' in browser.contents


@pytest.fixture('function')
def po_date_webdriver():
    """Webdriver page object for the date widget."""
    class PODate(WebdriverPageObjectBase):
        paths = [
            'PERSON_ADD_URL',
            'PERSONS_LIST_URL',
        ]

        def select_first_of_month(self):
            self._selenium.click('css=.date-field')
            self._selenium.click("link=1")

        def save(self):
            # Fill in required fields:
            self._selenium.type(
                'id=IcemacAddressbookPersonPerson-widgets-'
                'IcemacAddressbookPersonPerson-last_name', 'Tester')
            self._selenium.click("id=form-buttons-add")

    Webdriver.attach(PODate, 'date')
    yield
    Webdriver.detach(PODate, 'date')


@pytest.mark.webdriver
def test_form__DateWidget__1_webdriver(address_book, po_date_webdriver, webdriver):  # noqa
    """It renders a JavaScript calendar."""
    date = webdriver.date
    webdriver.login('editor', date.PERSON_ADD_URL)
    webdriver.windowMaximize()
    date.select_first_of_month()
    date.save()
    # Successful apply leads back to keyword overview
    assert date.PERSONS_LIST_URL == webdriver.path


def test_form__DateWidget__2(address_book, browser):
    """It renders a JavaScript calendar. (test for coverage)"""
    browser.login('editor')
    browser.open(browser.PERSON_ADD_URL)
    assert '"dateFormat": "yy M d "' in browser.contents


def test_form__FieldDescriptionAsHint__get__1(zcmlS):
    """It returns the ComputedWidgetAttribute `hint` if it is registered."""
    obj = FieldDescriptionAsHint(
        field=zope.dublincore.interfaces.IDCTimes['modified'],
        context=None, request=None, form=None, widget=None)
    result = obj.get()
    assert ('The date and time that the object was last modified '
            'converted to the displayed time zone.' == result)
    assert isinstance(result, zope.i18nmessageid.Message)


def test_form__FieldDescriptionAsHint__get__2(address_book, FieldFactory):
    """It returns the description of a user defined field.

    It replaces newlines by spaces as the description is put into a TextLine
    field later on.
    """
    field = FieldFactory(
        address_book, icemac.addressbook.interfaces.IKeyword, u'Bool',
        u'usable?', notes=u'Is\nthis\rkeyword\r\nusable?')
    obj = FieldDescriptionAsHint(
        field=zope.schema.interfaces.IField(field),
        context=None, request=None, form=None, widget=None)
    result = obj.get()
    assert ('Is this keyword  usable?' == result)
    assert isinstance(result, six.text_type)
