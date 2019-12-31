from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from six.moves.urllib_parse import urlsplit
import collections
import datetime
import gocept.jslint
import icemac.addressbook.addressbook
import icemac.addressbook.interfaces
import icemac.addressbook.person
import icemac.addressbook.startup
import icemac.addressbook.utils
import lxml.etree
import os
import plone.testing
import plone.testing.zca
import plone.testing.zodb
import pytest
import pytz
import selenium.webdriver.support.ui
import transaction
import z3c.etestbrowser.testing
import zope.app.publication.zopepublication
import zope.app.wsgi.testlayer
import zope.component
import zope.component.hooks
import zope.i18n
import zope.testbrowser.browser
import zope.testbrowser.interfaces
import zope.testbrowser.wsgi


CURRENT_CONNECTION = None
ZODBConnection = collections.namedtuple(
    'ZODBConnection', ['connection', 'rootFolder', 'zodb'])


def createZODBConnection(zodbDB):
    """Create an open ZODB connection."""
    connection = zodbDB.open()
    rootFolder = connection.root()[
        zope.app.publication.zopepublication.ZopePublication.root_name]
    return ZODBConnection(connection, rootFolder, zodbDB)


def pyTestEmptyZodbFixture():
    """Create an empty ZODB prepared to create an address book inside.

    Yields the zodb object.

    Prepared to be usable with a ``pytest.yield_fixture()``.

    """
    layer = plone.testing.zodb.EmptyZODB()
    layer.setUp()
    zodb = layer['zodbDB']
    zope.event.notify(zope.processlifetime.DatabaseOpened(zodb))
    transaction.commit()
    yield zodb
    layer.tearDown()


def pyTestAddressBookFixture(zodb, name):
    """Create an address book in the ZODB.

    Expects an empty ZODB as created by pyTestEmptyZodbFixture() and a name
    for the demo storage layer.

    Yields the zodb object.

    Prepared to be usable with a ``pytest.yield_fixture()``.

    """
    for connection in pyTestStackDemoStorage(zodb, name):
        icemac.addressbook.testing.create_addressbook(
            connection.rootFolder, name='ab', title=u'test addressbook')
        transaction.commit()
        yield connection.zodb


def pyTestStackDemoStorage(zodb, name):
    """Put a demo storage on top of ``zodb`` and yield the connection tuple.

    Prepared to be usable with a ``pytest.yield_fixture()``.

    """
    global CURRENT_CONNECTION
    storage = plone.testing.zodb.stackDemoStorage(zodb, name=name)
    connection = icemac.addressbook.testing.createZODBConnection(storage)
    transaction.begin()
    CURRENT_CONNECTION = connection
    yield connection
    storage.close()
    transaction.abort()
    connection.connection.close()
    CURRENT_CONNECTION = None


def site(connection):
    """Get the address book from the connection and set it as site.

    Usable in a `yield_fixture`.
    Resets the site to its previous value at exit.

    """
    addressbook = connection.rootFolder['ab']
    with zope.component.hooks.site(addressbook):
        yield addressbook


# Layer factories


def SecondaryZCMLLayer(
        name, module, package, bases=(), filename="ftesting.zcml"):
    """Factory to create a new ZCML test layer above an existing one."""
    return plone.testing.zca.ZCMLSandbox(
        name="%sZCML" % name, bases=bases, filename=filename,
        module=module, package=package)


# Test cases

class JSLintTest(gocept.jslint.TestCase):
    """Base test class for JS lint tests."""

    jshint_command = os.environ.get('JSHINT_COMMAND', '/bin/false')
    options = (gocept.jslint.TestCase.options + (
               'evil',
               'eqnull',
               'multistr',
               'sub',
               'undef',
               'browser',
               'jquery',
               'devel'
               ))


# List of users those passwords are not equal to the login name:
USERNAME_PASSWORD_MAP = dict(
    mgr='mgrpw',
    globalmgr='globalmgrpw'
)


class Browser(z3c.etestbrowser.testing.ExtendedTestBrowser):
    """Enriched test browser."""

    ROOT_URL_WITHOUT_SLASH = 'http://localhost'
    ROOT_URL = 'http://localhost/'
    # The login URL starts with this string:
    LOGIN_BASE_URL = 'http://localhost/ab/@@loginForm.html?camefrom=http'
    SELENIUM_LOGIN_URL = 'http://localhost/selenium-login'

    ADDRESS_BOOK_DEFAULT_URL = 'http://localhost/ab'
    ADDRESS_BOOK_ADD_URL = 'http://localhost/@@addAddressBook.html'
    ADDRESS_BOOK_WELCOME_URL = 'http://localhost/ab/@@welcome.html'
    ADDRESS_BOOK_2_WELCOME_URL = 'http://localhost/AddressBook/@@welcome.html'
    ADDRESS_BOOK_EDIT_URL = 'http://localhost/ab/@@edit-address_book.html'
    ADDRESS_BOOK_DELETE_PERSONS_URL = (
        'http://localhost/ab/@@delete-address_book-content.html')
    ADDRESS_BOOK_DELETE_URL = 'http://localhost/ab/@@delete-address_book.html'

    MASTER_DATA_URL = 'http://localhost/ab/@@masterdata.html'

    ENTITIES_EDIT_URL = 'http://localhost/ab/++attribute++entities'
    ENTITY_PERSON_LIST_FIELDS_URL = (
        'http://localhost/ab/++attribute++entities/'
        'icemac.addressbook.person.Person')
    ENTITY_PERSON_ADD_FIELD_URL = (
        'http://localhost/ab/++attribute++entities/'
        'icemac.addressbook.person.Person/@@addField.html')
    ENTITIY_PERSON_EDIT_FIELD_URL = (
        'http://localhost/ab/++attribute++entities/'
        'icemac.addressbook.person.Person/Field-1')
    ENTITIY_PERSON_DELETE_FIELD_URL = (
        'http://localhost/ab/++attribute++entities/'
        'icemac.addressbook.person.Person/Field-1/@@delete.html')
    ENTITIY_PERSON_CUSTOMIZE_FIELD_URL = (
        'http://localhost/ab/++attribute++entities/'
        'icemac.addressbook.person.Person/first_name')

    KEYWORDS_LIST_URL = 'http://localhost/ab/++attribute++keywords'
    KEYWORD_ADD_URL = (
        'http://localhost/ab/++attribute++keywords/@@addKeyword.html')
    KEYWORD_EDIT_URL = 'http://localhost/ab/++attribute++keywords/Keyword'
    KEYWORD_DELETE_URL = (
        'http://localhost/ab/++attribute++keywords/Keyword/@@delete.html')

    PERSON_ADD_URL = 'http://localhost/ab/@@addPerson.html'
    PERSON_CLONE_URL = 'http://localhost/ab/Person/@@clone.html'
    PERSON_EDIT_URL = 'http://localhost/ab/Person'
    PERSONS_LIST_URL = 'http://localhost/ab/@@person-list.html'
    PERSON_DELETE_URL = 'http://localhost/ab/Person/@@delete_person.html'
    PERSON_ARCHIVE_URL = 'http://localhost/ab/Person/@@archive_person.html'
    UNARCHIVE_PERSON_CONFIRM_URL = (
        'http://localhost/ab/++attribute++archive/Person/@@unarchive.html')
    PERSON_DELETE_ENTRY_URL = (
        'http://localhost/ab/Person/@@delete_entry.html')
    PERSON_EXPORT_URL = 'http://localhost/ab/Person/@@export.html'

    POSTAL_ADDRESS_DELETE_URL = (
        'http://localhost/ab/Person/PostalAddress-2/@@delete.html')
    PHONE_NUMBER_DELETE_URL = (
        'http://localhost/ab/Person/PhoneNumber-2/@@delete.html')
    EMAIL_ADDRESS_DELETE_URL = (
        'http://localhost/ab/Person/EMailAddress-2/@@delete.html')
    HOMEPAGE_ADDRESS_DELETE_URL = (
        'http://localhost/ab/Person/HomePageAddress-2/@@delete.html')

    FILE_ADD_URL = 'http://localhost/ab/Person/@@addFile.html'
    FILE_DELETE_URL = 'http://localhost/ab/Person/File/@@delete.html'
    FILE_DOWNLOAD_URL = 'http://localhost/ab/Person/File/download.html'

    PRINCIPALS_LIST_URL = 'http://localhost/ab/++attribute++principals'
    PRINCIPAL_ADD_URL = (
        'http://localhost/ab/++attribute++principals/@@addPrincipal.html')
    PRINCIPAL_EDIT_URL = 'http://localhost/ab/++attribute++principals/2'
    PRINCIPAL_EDIT_URL_1 = 'http://localhost/ab/++attribute++principals/1'
    PRINCIPAL_DELETE_URL = (
        'http://localhost/ab/++attribute++principals/2/@@delete_user.html')
    PRINCIPAL_DELETE_URL_1 = (
        'http://localhost/ab/++attribute++principals/1/@@delete_user.html')

    SEARCH_URL = 'http://localhost/ab/@@search.html'
    SEARCH_BY_NAME_URL = 'http://localhost/ab/@@name_search.html'
    SEARCH_BY_KEYWORD_URL = 'http://localhost/ab/@@multi_keyword.html'
    SEARCH_MULTI_UPDATE_URL = 'http://localhost/ab/@@multi-update'
    SEARCH_MULTI_UPDATE_CHOOSE_FIELD_URL = (
        'http://localhost/ab/multi-update/chooseField')
    SEARCH_MULTI_UPDATE_ENTER_VALUE_URL = (
        'http://localhost/ab/multi-update/enterValue')
    SEARCH_MULTI_UPDATE_CHECK_RESULT_URL = (
        'http://localhost/ab/multi-update/checkResult')
    SEARCH_MULTI_UPDATE_COMPLETE_URL = (
        'http://localhost/ab/@@multi-update-completed')
    SEARCH_ARCHIVE_URL = 'http://localhost/ab/@@archive_persons.html'
    SEARCH_DELETE_URL = 'http://localhost/ab/@@delete_persons.html'

    PREFS_URL = 'http://localhost/ab/++preferences++/ab'
    PREFS_TIMEZONE_URL = (
        'http://localhost/ab/++preferences++/ab.timeZone/@@index.html')

    ARCHIVE_URL = ADDRESS_BOOK_DEFAULT_URL + '/++attribute++archive'
    ARCHIVE_PERSON_URL = ARCHIVE_URL + '/Person'

    INSPECTOR_VIEW_URL = PERSONS_LIST_URL + '/@@inspector'
    INSPECTOR_OBJECT_URL = KEYWORDS_LIST_URL + '/@@inspector'
    INSPECTOR_ROOT_OBJECT_URL = ROOT_URL + '/@@inspector'

    def login(self, username, password=None):
        """Login a user using basic auth."""
        password = USERNAME_PASSWORD_MAP.get(username, username)
        self.addHeader(
            'Authorization', 'Basic {username}:{password}'.format(
                username=username, password=password))
        return self

    def formlogin(self, username, password, use_current_url=False):
        """Login using the login form."""
        if not use_current_url:
            self.open(self.ADDRESS_BOOK_DEFAULT_URL)
        self.getControl('User Name').value = username
        self.getControl('Password').value = password
        self.getControl('Log in').click()
        assert 'You have been logged-in successfully.' == self.message, \
            'Not successfully logged in: message={0.message!r}'.format(self)
        return self

    def logout(self):
        """Logout from the address book."""
        self.getLink('Logout').click()
        self.html_redirect()
        assert 'You have been logged out successfully.' in self.message, \
            'Not successfully logged out: message={0.message!r}'.format(self)

    def lang(self, lang):
        """Set the language for the browser."""
        self.addHeader('Accept-Language', lang)

    def open(self, url, **kw):
        super(Browser, self).open(url, **kw)
        return self

    @property
    def contents_without_whitespace(self):
        """Browser contents but with removed whitespace."""
        return self.contents.replace(' ', '').replace('\n', '')

    def etree_to_list(self, etree):
        """"Convert an etree into a list (lines without leading whitespace.)"""
        return [x.strip()
                for x in lxml.etree.tostring(etree).split('\n')
                if x.strip()]

    @property
    def message(self):
        """Return the info messages displayed in browser.

        Returns string when there is exactly one message, list otherwise.
        """
        messages = [x.text
                    for x in self.etree.xpath(
                        '//div[@id="info-messages"]/ul/li')]
        if len(messages) == 1:
            return messages[0]
        return messages

    def keyword_search(self, keyword, apply=None):
        """Search for a keyword via keyword-search.

        If `apply` is not `None` select the value from the dropdown and submit
        the search result handler.

        """
        self.open(self.SEARCH_BY_KEYWORD_URL)
        self.getControl('keywords').displayValue = [keyword]
        self.getControl('Search').click()
        if apply:
            self.getControl('Apply on selected persons').displayValue = [apply]
            self.getControl(name='form.buttons.apply').click()

    @property
    def submit_control_names(self):
        """List of the names of the submit controls in the form."""
        return self._get_control_names(
            zope.testbrowser.interfaces.ISubmitControl, self.getForm())

    @property
    def submit_control_names_all_forms(self):
        """List of the names of the submit controls in all forms."""
        forms = [self.getForm(index=index)
                 for index, _ in enumerate(self._getAllResponseForms())]
        names = [
            self._get_control_names(
                zope.testbrowser.interfaces.ISubmitControl, x)
            for x in forms]
        return names

    @property
    def all_control_names(self):
        """List of the names of all controls in the form."""
        return self._get_control_names(
            zope.testbrowser.interfaces.IControl, self.getForm())

    def html_redirect(self):
        """Redirect as requested by ``<meta http-equiv="refresh" ... />``."""
        soup = BeautifulSoup(self.contents, "lxml")
        meta = soup.find('meta', **{'http-equiv': 'refresh'})
        assert meta is not None, 'No <meta http-equiv="refresh" /> tag found.'
        url = meta.get('content').partition(';url=')[2]
        self.open(url)

    def select_favicon(self):
        """Select the first favicon."""
        icon = self.etree.xpath(
            '//li[@id="form-widgets-favicon-0"]')[0].attrib['data-value']
        self.getControl(name='form.widgets.favicon:list').value = icon

    def assert_forbidden(self, url):
        """Assert accessing a URL is forbidden for the current user."""
        with pytest.raises(zope.testbrowser.browser.HTTPError) as err:
            self.open(url)
        assert 'HTTP Error 403: Forbidden' == str(err.value), \
            'Raised "{}" instead of HTTP-403 Forbidden'.format(err.value)

    def _get_control_names(self, interface, form):
        """Get a sorted list of names of controls providing `interface`."""
        return sorted([control.name
                       for control in form.controls
                       if interface.providedBy(control)])


class WebdriverBase(object):  # pragma: no cover (webdriver)
    """Base for all Webdriver classes."""

    def __init__(self, selenium, address):
        self._selenium = selenium
        self._address = address


class Webdriver(WebdriverBase):  # pragma: no cover (webdriver)
    """Wrapper around Selenese."""

    _to_attach = []

    @classmethod
    def attach(cls, factory, attrib_name):
        """Attach a page object to an attribute of the instance."""
        cls._to_attach.append((factory, attrib_name))

    @classmethod
    def detach(cls, factory, attrib_name):
        """Detach a page object from an attribute of the instance."""
        cls._to_attach.remove((factory, attrib_name))

    def __init__(self, selenium, address):
        super(Webdriver, self).__init__(selenium, address)
        for factory, attrib_name in self._to_attach:
            setattr(self, attrib_name, factory(selenium, address))

    def login(self, username, target_path):
        transaction.commit()
        (_, _, path, _, _) = urlsplit(Browser.SELENIUM_LOGIN_URL)
        server = self._address
        password = USERNAME_PASSWORD_MAP.get(username, username)
        url = "http://{username}:{password}@{server}{path}".format(**locals())
        self._selenium.get(url)
        self.open(target_path)

    def open(self, path):
        url = "http://{server}{path}".format(server=self._address, path=path)
        self._selenium.get(url)

    @property
    def message(self):
        """Get the message even if it is no longer displayed."""
        return self._selenium.find_element_by_css_selector(
            '#info-messages li').get_attribute('textContent')

    @property
    def path(self):
        """Return the path of the current URL."""
        return self._selenium.current_url.replace(
            'http://{}'.format(self._address), '')

    def windowMaximize(self):
        self._selenium.set_window_size(1200, 800)


class WebdriverPageObjectBase(WebdriverBase):  # pragma: no cover (webdriver)
    """Base for page object classes to used with to ``Webdriver.attach()``."""

    browser = Browser  # Browser class to get URLs from
    paths = []  # URL attributes on `browser` to be converted to local paths

    def __init__(self, selenium, address):
        super(WebdriverPageObjectBase, self).__init__(selenium, address)
        for name in self.paths:
            url = getattr(self.browser, name)
            path = url.replace('http://localhost', '')
            assert getattr(self, name, None) is None, \
                'duplicate name {}'.format(name)
            setattr(self, name, path)

    def select_from_drop_down(
            self, title_or_titles, id=None, has_search_field=True):
        """Select elements with the given titles from the drop-down.

        `title_or_titles` can be a string or a list of strings.
        `id` can be a CSS ID of an out element.
        `has_search_field` ... set it to `False` if the drop down has no
                               search field. (Requires `id` not to be `None`!)
        """
        selector = self._get_drop_down_selector(id)
        self._selenium.find_element_by_css_selector(selector).click()
        values = (title_or_titles
                  if isinstance(title_or_titles, (tuple, list))
                  else [title_or_titles])
        for x in values:
            if has_search_field:
                self._selenium.find_element_by_css_selector(
                    ".select2-search__field").send_keys(str(x))
                self._selenium.find_element_by_css_selector(
                    ".select2-search__field").send_keys("\n")
            else:
                self._selenium.find_element_by_xpath(
                    '//ul[@class="select2-results__options"]'
                    '/li[contains(text(), "{}")]'.format(x)).click()

    def get_drop_down_selection(self, id=None):
        """Get the selected value of a drop down.

        `id` can be a CSS ID of an out element.
        """
        selector = self._get_drop_down_selector(id)
        return self._selenium.find_element_by_css_selector(selector).text

    def _get_drop_down_selector(self, id=None):
        selector = '.select2-selection__rendered'
        if id is not None:
            selector = '#{} {}'.format(id, selector)
        return selector


class TimeZoneMixIn(object):  # pragma: no cover (webdriver)
    """Mix-in for page objects to handle time zones."""

    @property
    def timezone(self):
        select = selenium.webdriver.support.ui.Select(
            self._selenium.find_element_by_id("form-widgets-time_zone"))
        return select.first_selected_option.text

    @timezone.setter
    def timezone(self, value):
        # Open drop down:
        self._selenium.find_element_by_css_selector(
            "#form-widgets-time_zone ~ span").click()
        # Select value:
        self._selenium.find_element_by_css_selector(
            '.select2-container--open input').send_keys(value + '\n')


class POAddressBook(WebdriverPageObjectBase, TimeZoneMixIn):
    """Webdriver page object for the address book itself."""

    paths = [
        'ADDRESS_BOOK_DEFAULT_URL',
        'ADDRESS_BOOK_EDIT_URL',
        'ADDRESS_BOOK_2_WELCOME_URL',
        'ROOT_URL',
        'SEARCH_URL',
    ]

    def create(self):
        # On the start page there is a link to add an address book:
        self._selenium.find_element_by_link_text('address book').click()

    @property
    def title(self):
        return self._selenium.find_element_by_id(
            'form-widgets-title').get_attribute('value')

    @title.setter
    def title(self, title):
        el = self._selenium.find_element_by_id('form-widgets-title')
        el.clear()
        el.send_keys(title)

    # setter property!
    def startpage(self, value):
        self.select_from_drop_down(
            value, id='form-widgets-startpage-row', has_search_field=False)

    startpage = property(None, startpage)

    def assert_default_favicon_selected(self):
        # Default value of favicon is pre-selected:
        assert 1 == len(self._selenium.find_elements_by_css_selector(
            '.ui-selected img[src="/++resource++img/favicon-red-preview.png"]'
        ))

    def select_favicon(self, index):
        el = self._selenium.find_element_by_id(
            'form-widgets-favicon-{}'.format(index))
        ac = ActionChains(self._selenium)
        ac.move_to_element(el).move_by_offset(20, 20).click().perform()

    def assert_favicon_selected(self, index):
        assert 1 == len(self._selenium.find_elements_by_css_selector(
            '#form-widgets-favicon-{}.ui-selected'.format(index)))

    def submit(self, name):
        self._selenium.find_element_by_id(
            'form-buttons-{}'.format(name)).click()


Webdriver.attach(POAddressBook, 'address_book')


class POPersonList(WebdriverPageObjectBase):
    """Webdriver page object for the person list page."""

    paths = []

    @property
    def column_headlines(self):
        """Get the headlines of the columns displayed on the person list."""
        elements = self._selenium.find_elements_by_xpath(
            '//div[@id="content"]/table/thead/tr/th/a')
        return [x.text for x in elements]


Webdriver.attach(POPersonList, 'personlist')


class POPreferences(WebdriverPageObjectBase, TimeZoneMixIn):
    """Webdriver page object for the preferences page."""

    paths = [
        'PREFS_URL',
    ]

    def open_time_zone_element(self):
        self._selenium.find_element_by_css_selector(
            "fieldset.timeZone").click()
        WebDriverWait(self._selenium, 10).until(
            EC.presence_of_element_located((By.ID, "form-widgets-time_zone")))

    def wait_for_fields_visible(self, visible):
        wait = WebDriverWait(self._selenium, 3)  # seconds
        if visible:
            attrib_name = 'until'
        else:
            attrib_name = 'until_not'
        return getattr(wait, attrib_name)(EC.visibility_of(
            self._selenium.find_element_by_id('form-widgets-columns-row')))

    def toggle_group(self, css_class):
        self._selenium.find_element_by_xpath(
            "//fieldset[@class='{}']/legend".format(css_class)).click()

    def remove_first_column_selected_for_person_list(self):
        self._selenium.find_element_by_css_selector(
            "span.select2-selection__choice__remove").click()
        # deselect column drop down
        self._selenium.find_element_by_css_selector(
            "ul.select2-selection__rendered").click()

    def select_column_for_person_list(self, title):
        self.select_from_drop_down(title)

    @property
    def selected_columns_for_person_list(self):
        selection = self._selenium.find_elements_by_xpath(
            '//div[@id="form-widgets-columns-row"]/div/span/span/span/ul/li')
        return [x.text.replace(u'\xd7', '')  # remove x used for delete link
                for x in selection
                if x.text]

    def submit(self):
        self._selenium.find_element_by_id("form-buttons-apply").click()


Webdriver.attach(POPreferences, 'prefs')


# assertion helper functions and helper classes


class SiteMenu(object):
    """Helper class to test selections in the site menu."""

    def __init__(self, browser, menu_item_index, menu_item_title,
                 menu_item_URL):
        """Parameters:

        browser ... return value of the ``browser`` fixture.
        menu_item_index ... zero-based index of the position of the item in
                             the menu
        menu_item_title ... title of the menu item
        menu_item_URL ... URL the menu item should point to

        """
        self.browser = browser
        self.menu_item_index = menu_item_index
        self.menu_item_title = menu_item_title
        self.menu_item_URL = menu_item_URL

    def item_selected(self, url):
        self.browser.open(url)
        return bool(
            self.browser.etree.xpath(self._xpath)[0].attrib.get('class'))

    def get_menu_item_title_under_test(self):
        self.browser.open(self.menu_item_URL)
        return self.browser.etree.xpath('%s/a/span' % self._xpath)[0].text

    @property
    def _xpath(self):
        # xpath is one based!
        return '//div[@class="menuToggle main-menu"]/ul/li[%s]' % (
            self.menu_item_index + 1)


class AddressBookAssertions:
    """Assertions helpful to check automatic installation routines."""

    def __init__(self, address_book):
        self.address_book = address_book

    def has_local_utility(self, iface, name=''):
        """Assert that there is a local utility for the given interface."""
        util = zope.component.queryUtility(
            iface, context=self.address_book, name=name)
        assert util is not None

    def has_attribute(self, attribute, iface, name=''):
        """Assert the address book has an attribute provided as utility."""
        assert iface.providedBy(getattr(self.address_book, attribute))
        self.has_local_utility(iface, name)


class DateTimeClass(object):
    """Helper class to create and format datetime objects."""

    @property
    def now(self):
        return pytz.utc.localize(datetime.datetime.utcnow())

    def format(self, dt, force_date=False):
        """Format a datetime to the format needed in testbrowser."""
        if isinstance(dt, datetime.datetime) and not force_date:
            return dt.strftime('%y/%m/%d %H:%M')
        else:
            return self.format_date(dt)

    def format_date(self, dt):
        return "{0.year} {0.month} {0.day} ".format(dt)

    @staticmethod
    def add(dt, days=0, seconds=0):
        """Add some days and/or seconds to `dt`."""
        return dt + datetime.timedelta(days=days, seconds=seconds)


# Helper functions to create objects in the database

def create_addressbook(parent, name, title=None):
    """Create an address book in `parent`."""
    ab = icemac.addressbook.utils.create_obj(
        icemac.addressbook.addressbook.AddressBook)
    if title is not None:
        ab.title = title
    parent[name] = ab
    return ab


def create(address_book, parent, interface, set_as_default=False, *args, **kw):
    """Create an object using an entity.

    interface ... interface of the object which should be created.
    """
    with zope.component.hooks.site(address_book):
        entity = icemac.addressbook.interfaces.IEntity(interface)
        name = icemac.addressbook.utils.create_and_add(
            parent, entity.getClass(), *args)
        obj = parent[name]
        for key, value in kw.items():
            field = entity.getField(key)
            context = field.interface(obj)
            field.set(context, value)
        if set_as_default:
            field = icemac.addressbook.person.get_default_field(
                entity.interface)
            field.set(parent, obj)
        zope.lifecycleevent.modified(obj)
    return obj


def set_modified(obj, *args):
    """Set the modification date of an object."""
    dt = datetime.datetime(*args, tzinfo=pytz.utc)
    zope.dublincore.interfaces.IZopeDublinCore(obj).modified = dt
    return dt


def delete_field(browser, field_name):
    """Delete a user defined field."""
    manager = browser.login('mgr')
    manager.open(
        browser.ENTITY_PERSON_LIST_FIELDS_URL +
        '/{}/@@delete.html'.format(field_name))
    manager.getControl('Yes').click()
    assert manager.message.endswith('" deleted.')


# Helper functions and classes


class NonCachingPublicationCache(object):
    """Replacement to prevent caching of ZODB connections."""

    def get(self, key):
        return None

    def __setitem__(self, key, value):
        """Do not cache!"""
        pass


class TestHTTPPublicationRequestFactory(
        zope.app.publication.httpfactory.HTTPPublicationRequestFactory):
    """RequestFactory which uses the global `CURRENT_CONNECTION`."""

    def __init__(self):
        super(TestHTTPPublicationRequestFactory, self).__init__(None)
        self._publication_cache = NonCachingPublicationCache()

    @property
    def _db(self):
        return CURRENT_CONNECTION.zodb

    @_db.setter
    def _db(self, value):
        """Ignoring `value` because the global one should always be used."""


def getRootFolder():
    """`TransactionMiddleware` expects a callable to get the root folder."""
    return CURRENT_CONNECTION.rootFolder


def interpolate_insted_of_translate(
        self, msgid, mapping=None, *args, **kw):  # pragma: no cover webdriver
    """Use interpolation instead of translation."""
    return zope.i18n.interpolate(msgid, mapping)


# Helper views

class SeleniumLogin(object):  # pragma: no cover (webdriver)
    """Allow basic auth log-in of global users.

    It prevents rendering an Unauthorized page.
    """

    def __call__(self):
        return 'Selenium login succeeded.'
