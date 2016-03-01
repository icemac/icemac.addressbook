# -*- coding: utf-8 -*-
import collections
import datetime
import gocept.jslint
import icemac.addressbook.addressbook
import icemac.addressbook.interfaces
import icemac.addressbook.person
import icemac.addressbook.utils
import lxml.etree
import os
import plone.testing
import plone.testing.zca
import pytz
import transaction
import z3c.etestbrowser.wsgi
import zope.app.publication.zopepublication
import zope.component
import zope.component.hooks
import zope.testbrowser.browser
import zope.testbrowser.interfaces


ZODBConnection = collections.namedtuple(
    'ZODBConnection', ['connection', 'rootFolder', 'zodb'])


def createZODBConnection(zodbDB):
    """Create an open ZODB connection."""
    connection = zodbDB.open()
    rootFolder = connection.root()[
        zope.app.publication.zopepublication.ZopePublication.root_name]
    return ZODBConnection(connection, rootFolder, zodbDB)


# Layer factories


def SecondaryZCMLLayer(name, module, package, bases, filename="ftesting.zcml"):
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
USERNAME_PASSWORD_MAP = dict(mgr='mgrpw')


class Browser(z3c.etestbrowser.wsgi.ExtendedTestBrowser):
    """Enriched test browser."""

    ROOT_URL = 'http://localhost'
    # The login URL starts with this string:
    LOGIN_BASE_URL = 'http://localhost/ab/@@loginForm.html?camefrom=http'

    ADDRESS_BOOK_DEFAULT_URL = 'http://localhost/ab'
    ADDRESS_BOOK_WELCOME_URL = 'http://localhost/ab/@@welcome.html'
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
    SEARCH_DELETE_URL = 'http://localhost/ab/@@delete_persons.html'

    PREFS_URL = 'http://localhost/ab/++preferences++/ab'
    PREFS_TIMEZONE_URL = (
        'http://localhost/ab/++preferences++/ab.timeZone/@@index.html')

    def login(self, username, password=None):
        """Login a user using basic auth."""
        if password is None:
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
        assert 'You have been logged-in successfully.' == self.message
        return self

    def lang(self, lang):
        """Set the language for the browser."""
        self.addHeader('Accept-Language', lang)

    def open(self, url):
        super(Browser, self).open(url)
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
        forms = [self.getForm(index=x)
                 for x in range(len(list(self.mech_browser.forms())))]
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

    def in_out_widget_select(self, control_name, select_controls):
        """Add a selection to an in-out-widget.

        control_name ... name of the in-out-control, something like
                         'form.widgets.columns'
        select_controls ... list of control instances (item controls of in or
                             out list) which should be selected
        """
        form = self.getForm()
        for control in select_controls:
            form.mech_form.new_control(
                type='hidden',
                name='%s:list' % control_name,
                attrs=dict(value=control.optionValue))

    def _get_control_names(self, interface, form):
        """Get a sorted list of names of controls providing `interface`."""
        names = []
        for ctrl in form.mech_form.controls:
            control = zope.testbrowser.browser.controlFactory(ctrl, form, self)
            if interface.providedBy(control):
                names.append(control.name)
        return sorted(names)


class Webdriver(object):
    """Wrapper around Selenese."""

    def __init__(self, selenium):
        self.selenium = selenium

    def login(self, username):
        transaction.commit()
        sel = self.selenium
        sel.open("http://{username}:{password}@{server}/".format(
                 username=username, server=self.selenium.server,
                 password=USERNAME_PASSWORD_MAP.get(username, username)))
        return sel

    @property
    def message(self):
        return self.selenium.getText('css=#info-messages')


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
