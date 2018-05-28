from icemac.addressbook.install import not_matched_prerequisites, Configurator
from io import BytesIO
import contextlib
import os
import pytest
import six
import sys


# Fixtures


@pytest.fixture('function')
def basedir(tmpdir):
    """Create a base directory for the tests and chdir to it."""
    cwd = os.getcwd()
    tmpdir.chdir()
    yield tmpdir
    os.chdir(cwd)


@pytest.fixture(scope='function')
def install_default_ini(basedir):
    """Create an `install.default.ini` for `Configurator`."""
    install_default_ini = basedir.join('install.default.ini')
    install_default_ini.write("""\
[install]
eggs_dir = py-eggs

[admin]
login = me
password = secret

[server]
host = my.computer.local
port = 13090
username =

[log]
handler = FileHandler
max_size = 1000
when = midnight
interval = 1
backups = 5

[packages]

[migration]
do_migration = no
stop_server = no
start_server = no
""")


@pytest.fixture(scope='function')
def config(install_default_ini):
    """Return a `Configurator` instance running on `install.default.ini`."""
    config = Configurator(stdin=BytesIO())
    config.load()
    return config


@contextlib.contextmanager
def user_input(input, config):
    r"""Write `input` on `stdin`.

    If `input` is a list, join it using `\n`.
    """
    # Remove possibly existing previous input:
    config.stdin.seek(0)
    config.stdin.truncate()
    if not isinstance(input, six.string_types):
        input = '\n'.join(input)
    config.stdin.write(input)
    config.stdin.seek(0)
    yield


def test_install__not_matched_prerequisites__1(basedir):
    """It returns an error text if `buildout.cfg` already exists in `cwd`."""
    buildout_cfg = basedir.join('buildout.cfg')
    buildout_cfg.write('[buildout]')
    assert ('ERROR: buildout.cfg already exists.\n'
            '       Please (re-)move the existing one and restart install.' ==
            not_matched_prerequisites())


def test_install__not_matched_prerequisites__2(basedir):
    """It returns `False`:

    * if no `buildout.cfg` exists in `cwd` and
    * if the right python version is used.

    We expect that the version of the python which runs the tests matches the
    requirement.
    """
    assert False is not_matched_prerequisites()


def test_install__not_matched_prerequisites__3(monkeypatch, basedir):
    """It returns an error text for a too old python version.

    `icemac.addressbook` currently only runs with some Python versions. If
    another version is used, an error message is returned.
    """
    monkeypatch.setattr("sys.version_info", (2, 5, 6, 'final', 0))
    assert ('ERROR: icemac.addressbook currently supports only Python 2.7.'
            '\n       But you try to install it using Python 2.5.6.' ==
            not_matched_prerequisites())


def test_install__not_matched_prerequisites__4(monkeypatch, basedir):
    """It returns an error text for a too new python version."""
    monkeypatch.setattr("sys.version_info", (3, 0, 0, 'final', 0))
    assert ('ERROR: icemac.addressbook currently supports only Python 2.7.'
            '\n       But you try to install it using Python 3.0.0.' ==
            not_matched_prerequisites())


def test_install__Configurator__1(config):
    """It reads the default values from `install.default.ini`.

    An instance of this class reads the default configuration file
    (`install.default.ini`). Whose values are used when the user does not enter
    a value.
    """
    assert 'py-eggs' == config.get('install', 'eggs_dir')


def test_install__Configurator__2(config):
    """It stores the path to the old instance. By default it is empty."""
    assert '' == config.get('migration', 'old_instance')


def test_install__Configurator__3():
    """It uses `sys.stdin` if it is not explicitly set."""
    config = Configurator()
    assert sys.stdin == config.stdin


def test_install__Configurator__ask_user__1(config, capsys):
    """It asks for input from the user.

    It displays the default value as set in the configuration file. The entered
    value is stored in the configuration and is also returned. When the user
    does not enter a value (only hits `enter`), the default value is used
    instead.
    """
    with user_input('\n', config):
        config.ask_user('Server port', 'server', 'port')
    assert (u' Server port: [13090] \n', u'') == capsys.readouterr()
    assert '13090' == config.get('server', 'port')


def test_install__Configurator__ask_user__3(config, capsys):
    """It prefers the user entered value over the one in default config."""
    with user_input('4711', config):
        config.ask_user('Server port', 'server', 'port')
    with user_input('0815', config):
        config.ask_user('Server port', 'server', 'port')
    assert ((u' Server port: [13090] \n Server port: [4711] \n', u'') ==
            capsys.readouterr())
    assert '0815' == config.get('server', 'port')


def test_install__Configurator__ask_user__4(config, capsys):
    """It allows force entering a value of a list.

    It retries to get an answer until the user entered a value is contained in
    the list of allowed values.
    """
    with user_input(['maybe', '???', 'yes'], config):
        config.ask_user(
            'Really', 'migration', 'do_migration', values=('yes', 'no'))
    assert ([u' Really: [no] ',
             u"ERROR: 'maybe' is not in ('yes', 'no').",
             u'Please choose a value out of the list.',
             u' Really: [no] ',
             u"ERROR: '???' is not in ('yes', 'no').",
             u'Please choose a value out of the list.',
             u' Really: [no] '] == capsys.readouterr()[0].splitlines())
    assert 'yes' == config.get('migration', 'do_migration')


def test_install__Configurator__load__1(config):
    """It (Re-) loads the configuration from the configuration file(s)."""
    with user_input('4711', config):
        config.ask_user('Server port', 'server', 'port')
    assert '4711' == config.get('server', 'port')
    config.load()
    assert '13090' == config.get('server', 'port')


def test_install__Configurator__load__2(config):
    """It raises an error if `user_config` points to a not existing file."""
    config.user_config = 'i-do-not-exist.ini'
    with pytest.raises(IOError) as err:
        config.load()
    assert "'i-do-not-exist.ini' does not exist." == str(err.value)


def test_install__Configurator__load__3(config, basedir):
    """It assures that user configuration takes precedence over default."""
    assert 'py-eggs' == config.get('install', 'eggs_dir')
    user_ini = basedir.mkdir('prev_version').join('install.user.ini')
    user_ini.write("[install]\neggs_dir = my-eggs")
    config.user_config = str(user_ini)
    config.load()
    assert 'my-eggs' == config.get('install', 'eggs_dir')
    assert (str(basedir.join('prev_version')) ==
            config.get('migration', 'old_instance'))


def test_install__Configurator__load__4(config, basedir):
    """Resetting the user_config to `None` clears `old_instance` path."""
    user_ini = basedir.mkdir('prev_version').join('install.user.ini')
    user_ini.write('')

    config.user_config = str(user_ini)
    config.load()
    assert '' != config.get('migration', 'old_instance')

    config.user_config = None
    config.load()
    assert '' == config.get('migration', 'old_instance')


def test_install__Configurator__print_intro__1(config, capsys):
    """It prints an introduction text to stdout."""
    config.print_intro()
    assert ([
        u'Welcome to icemac.addressbook installation',
        u'',
        u'Hint: to use the default value (the one in [brackets]), '
        u'enter no value.',
        u''] == capsys.readouterr()[0].splitlines())


def test_install__Configurator__get_global_options__1(config, capsys):
    """It ask the user about global options and stores them."""
    with user_input('/Users/mac', config):
        config.get_global_options()
    assert (' Directory to store python eggs: [py-eggs] \n' ==
            capsys.readouterr()[0])
    assert '/Users/mac' == config.eggs_dir
    assert '/Users/mac' == config.get('install', 'eggs_dir')


def test_install__Configurator__get_server_options__1(config, capsys):
    """It asks the user about the server and store the answers."""
    with user_input(['admin', 'geheim', 'localhost', '8080', 'mac'], config):
        config.get_server_options()
    assert ([
        u' Log-in name for the administrator: [me] ',
        u' Password for the administrator: [secret] ',
        u' Hostname: [my.computer.local] ',
        u' Port number: [13090] ',
        u' Username whether process should run as different user otherwise '
        u'emtpy: [] ',
    ] == capsys.readouterr()[0].splitlines())
    assert 'admin' == config.admin_login
    assert 'admin' == config.get('admin', 'login')
    assert 'geheim' == config.admin_passwd
    assert 'geheim' == config.get('admin', 'password')
    assert 'localhost' == config.host
    assert 'localhost' == config.get('server', 'host')
    assert '8080' == config.port
    assert '8080' == config.get('server', 'port')
    assert 'mac' == config.username
    assert 'mac' == config.get('server', 'username')


def test_install__Configurator__get_log_options__1(config, capsys):
    """It asks the user about logging and store his answers.

    When the user enters a wrong handler name he is asked to enter it again.
    Choosing `TimedRotatingFileHandler` three additional questions are asked.
    """
    with user_input(['does not matter', 'TimedRotatingFileHandler', 'D', '7',
                     '8'], config):
        config.get_log_options()
    assert ([
        u' Please choose Log-Handler:',
        u'    Details see http://docs.python.org/library/logging.html#'
        u'handler-objects',
        u' Log-Handler, choose between FileHandler, RotatingFileHandler, '
        u'TimedRotatingFileHandler: [FileHandler] ',
        u"ERROR: 'does not matter' is not in ('FileHandler', "
        u"'RotatingFileHandler', 'TimedRotatingFileHandler').",
        u'Please choose a value out of the list.',
        u' Log-Handler, choose between FileHandler, RotatingFileHandler, '
        u'TimedRotatingFileHandler: [FileHandler] ',
        u' Type of rotation interval, choose between S, M, H, D, W, '
        u'midnight: [midnight] ',
        u' Rotation interval size: [1] ',
        u' Number of log file backups: [5] ',
    ] == capsys.readouterr()[0].splitlines())
    assert 'TimedRotatingFileHandler' == config.log_handler
    assert 'TimedRotatingFileHandler' == config.get('log', 'handler')
    assert 'D' == config.log_when
    assert 'D' == config.get('log', 'when')
    assert '7' == config.log_interval
    assert '7' == config.get('log', 'interval')
    assert '8' == config.log_backups
    assert '8' == config.get('log', 'backups')


def test_install__Configurator__get_log_options__2(config, capsys):
    """It asks the user about logging and store his answers.

    Choosing `RotatingFileHandler` two more questions are asked.
    """
    with user_input(['RotatingFileHandler', '12345', '2'], config):
        config.get_log_options()
    assert ([
        u' Please choose Log-Handler:',
        u'    Details see http://docs.python.org/library/logging.html#'
        u'handler-objects',
        u' Log-Handler, choose between FileHandler, RotatingFileHandler, '
        u'TimedRotatingFileHandler: [FileHandler] ',
        u' Maximum file size before rotating in bytes: [1000] ',
        u' Number of log file backups: [5] ',
    ] == capsys.readouterr()[0].splitlines())
    assert 'RotatingFileHandler' == config.log_handler
    assert 'RotatingFileHandler' == config.get('log', 'handler')
    assert '12345' == config.log_max_bytes
    assert '12345' == config.get('log', 'max_size')
    assert '2' == config.log_backups
    assert '2' == config.get('log', 'backups')


def test_install__Configurator__get_log_options__3(config, capsys):
    """It asks the user about logging and store his answers.

    Choosing `FileHandler` no more questions are asked:
    """
    with user_input('FileHandler', config):
        config.get_log_options()
    assert ([
        u' Please choose Log-Handler:',
        u'    Details see http://docs.python.org/library/logging.html#'
        u'handler-objects',
        u' Log-Handler, choose between FileHandler, RotatingFileHandler, '
        u'TimedRotatingFileHandler: [FileHandler] ',
    ] == capsys.readouterr()[0].splitlines())
    assert 'FileHandler' == config.log_handler
    assert 'FileHandler' == config.get('log', 'handler')


def test_install__Configurator__print_additional_packages_intro__1(
        config, capsys):
    """It prints the introduction text for additional packages."""
    config.print_additional_packages_intro()
    assert ([
        u' When you need additional packages (e. g. import readers)',
        u' enter the package names here separated by a newline.',
        u' When you are done enter an empty line.',
        u' Known packages:',
        u'   icemac.ab.importer -- Import of CSV files',
        u'   icemac.ab.importxls -- Import of XLS (Excel) files',
        u'   icemac.ab.calendar -- Calendar using persons in address book',
    ] == capsys.readouterr()[0].splitlines())


def test_install__Configurator__get_additional_packages__1(config, capsys):
    """It asks for the names of additional packages.

    Those packages are later added as runtime and test dependenies. They need a
    `configure.zcml` as they get integrated using that file.
    """
    with user_input(['icemac.ab.importxls', 'icemac.ab.importcsv'], config):
        config.get_additional_packages()
    assert ([
        u' Package 1: [] ',
        u' Package 2: [] ',
        u' Package 3: [] ',
    ] == capsys.readouterr()[0].splitlines())
    assert ['icemac.ab.importxls', 'icemac.ab.importcsv'] == config.packages
    assert 'icemac.ab.importxls' == config.get('packages', 'package_1')
    assert 'icemac.ab.importcsv' == config.get('packages', 'package_2')
    assert '' == config.get('packages', 'package_3')


def test_install__Configurator__get_migration_options__1(config, capsys):
    """It ask the user about the migration of existing content.

    It stores the values. When the user decides no to do the migration no
    additional questions are asked.
    """
    with user_input('no', config):
        config.get_migration_options()
    assert (u'  Migrate old address book content to new instance: [no] \n' ==
            capsys.readouterr()[0])
    assert 'no' == config.do_migration
    assert 'no' == config.get('migration', 'do_migration')


def test_install__Configurator__get_migration_options__2(config, capsys):
    """It ask the user about the migration of existing content.

    When the user chooses to migrate he is asked some additional questions.
    """
    with user_input(['yes', 'no', 'yes'], config):
        config.get_migration_options()
    assert ([
        u'  Migrate old address book content to new instance: [no] ',
        u'The old address book instance must not run during migration.',
        u'When it runs as demon process the migration script can stop it '
        u'otherwise you have to stop it manually.',
        u' Old instance is running as a demon process: [no] ',
        u' New instance should be started as a demon process after migration: '
        u'[no] ',
    ] == capsys.readouterr()[0].splitlines())
    assert 'yes' == config.do_migration
    assert 'yes' == config.get('migration', 'do_migration')
    assert 'no' == config.stop_server
    assert 'no' == config.get('migration', 'stop_server')
    assert 'yes' == config.start_server
    assert 'yes' == config.get('migration', 'start_server')


def test_install__Configurator__create_admin_zcml__1(config, capsys, basedir):
    """It creates the `admin.zcml` file.

    This file which contains the password of the global administrator.
    """
    config.admin_login = 'root'
    config.admin_passwd = 'keins'
    config.create_admin_zcml()
    assert 'creating admin.zcml ...\n' == capsys.readouterr()[0]
    assert [
        '<configure xmlns="http://namespaces.zope.org/zope">',
        '  <principal',
        '    id="icemac.addressbook.global.Administrator"',
        '    title="global administrator"',
        '    login="root"',
        '    password_manager="Plain Text"',
        '    password="keins" />',
        '  <grant',
        '    role="icemac.addressbook.global.Administrator"',
        '    principal="icemac.addressbook.global.Administrator" />',
        '  <grant',
        '    permission="zope.ManageContent"',
        '    principal="icemac.addressbook.global.Administrator" />',
        '</configure>',
    ] == basedir.join('admin.zcml').read().splitlines()


def test_install__Configurator__create_buildout_cfg__1(
        config, capsys, basedir):
    """It creates the `buildout.cfg` file.

    This file contains the user configurations for the server. The contents of
    the file depend a bit on the chosen log handler.
    """
    config.eggs_dir = '/var/lib/eggs'
    config.host = 'server.local'
    config.port = '8081'
    config.username = ''
    config.log_handler = 'FileHandler'
    config.packages = ['icemac.ab.reporting', 'icemac.ab.relations']
    config.create_buildout_cfg()
    assert 'creating buildout.cfg ...\n' == capsys.readouterr()[0]
    assert [
        '[buildout]',
        'extends = profiles/prod.cfg',
        'newest = true',
        'allow-picked-versions = true',
        'eggs-directory = /var/lib/eggs',
        'index = https://pypi.python.org/simple',
        '',
        '[deploy.ini]',
        'host = server.local',
        'port = 8081',
        'log-handler = FileHandler',
        "log-handler-args = 'a'",
        '',
        '[site.zcml]',
        'permissions_zcml = <include package="icemac.ab.reporting" />',
        '\t<include package="icemac.ab.relations" />',
        '',
        '[app]',
        'eggs += icemac.ab.reporting',
        '      icemac.ab.relations',
        '',
        '[test]',
        'eggs += icemac.ab.reporting',
        '      icemac.ab.relations',
        ''
    ] == basedir.join('buildout.cfg').read().splitlines()


def test_install__Configurator__create_buildout_cfg__2(
        config, capsys, basedir):
    """It creates the `buildout.cfg` file.

    Using different log handler results in different ``log-handler-args``.
    """
    config.log_handler = 'RotatingFileHandler'
    config.log_max_bytes = '200000'
    config.log_backups = '10'
    config.eggs_dir = 'eggs'
    config.host = 'host'
    config.port = 'port'
    config.username = ''
    config.packages = []
    config.create_buildout_cfg()
    assert 'creating buildout.cfg ...\n' == capsys.readouterr()[0]
    assert ("log-handler-args = 'a', 200000, 10" in
            basedir.join('buildout.cfg').read())


def test_install__Configurator__create_buildout_cfg__3(
        config, capsys, basedir):
    """It creates the `buildout.cfg` file.

    Using `TimedRotatingFileHandler` results in different ``log-handler-args``.
    """
    config.log_handler = 'TimedRotatingFileHandler'
    config.log_when = 'W'
    config.log_interval = '2'
    config.log_backups = '1'
    config.eggs_dir = 'eggs'
    config.host = 'host'
    config.port = 'port'
    config.username = ''
    config.packages = []
    config.create_buildout_cfg()
    assert 'creating buildout.cfg ...\n' == capsys.readouterr()[0]
    assert "log-handler-args = 'W', 2, 1" in basedir.join(
        'buildout.cfg').read()


def test_install__Configurator__create_buildout_cfg__4(
        config, capsys, basedir):
    """It creates the `buildout.cfg` file.

    When the username is not empty a zdaemon.conf section is added.
    """
    config.username = 'mac'
    config.log_handler = 'FileHandler'
    config.eggs_dir = 'eggs'
    config.host = 'host'
    config.port = 'port'
    config.packages = []
    config.create_buildout_cfg()
    assert 'creating buildout.cfg ...\n' == capsys.readouterr()[0]
    assert ("[zdaemon.conf]\nuser = user mac" in
            basedir.join('buildout.cfg').read())


def test_install__Configurator__store__1(config, capsys, basedir):
    """It stores the configuration values in a file named `install.user.ini`"""
    config.store()
    assert 'saving config ...\n' == capsys.readouterr()[0]
    assert [
        '[install]',
        'eggs_dir = py-eggs',
        '',
        '[admin]',
        'login = me',
        'password = secret',
        '',
        '[server]',
        'host = my.computer.local',
        'port = 13090',
        'username = ',
        '',
        '[log]',
        'handler = FileHandler',
        'max_size = 1000',
        'when = midnight',
        'interval = 1',
        'backups = 5',
        '',
        '[packages]',
        '',
        '[migration]',
        'do_migration = no',
        'stop_server = no',
        'start_server = no',
        'old_instance = ',
        '',
    ] == basedir.join('install.user.ini').read().splitlines()


def test_install__Configurator____call____1(config, capsys, basedir):
    """It runs the complete configuration.

    To ease testing changes we use only default values.
    """
    with user_input('', config):
        config()
    assert [
        'Welcome to icemac.addressbook installation',
        '',
        'Hint: to use the default value (the one in [brackets]), enter no '
        'value.',
        '',
        ' Directory to store python eggs: [py-eggs] ',
        ' Log-in name for the administrator: [me] ',
        ' Password for the administrator: [secret] ',
        ' Hostname: [my.computer.local] ',
        ' Port number: [13090] ',
        ' Username whether process should run as different user otherwise '
        'emtpy: [] ',
        ' Please choose Log-Handler:',
        '    Details see http://docs.python.org/library/logging.html#'
        'handler-objects',
        ' Log-Handler, choose between FileHandler, RotatingFileHandler, '
        'TimedRotatingFileHandler: [FileHandler] ',
        ' When you need additional packages (e. g. import readers)',
        ' enter the package names here separated by a newline.',
        ' When you are done enter an empty line.',
        ' Known packages:',
        '   icemac.ab.importer -- Import of CSV files',
        '   icemac.ab.importxls -- Import of XLS (Excel) files',
        '   icemac.ab.calendar -- Calendar using persons in address book',
        ' Package 1: [] ',
        '  Migrate old address book content to new instance: [no] ',
        'creating admin.zcml ...',
        'creating buildout.cfg ...',
        'saving config ...',
    ] == capsys.readouterr()[0].splitlines()
    assert [
        '[buildout]',
        'extends = profiles/prod.cfg',
        'newest = true',
        'allow-picked-versions = true',
        'eggs-directory = py-eggs',
        'index = https://pypi.python.org/simple',
        '',
        '[deploy.ini]',
        'host = my.computer.local',
        'port = 13090',
        'log-handler = FileHandler',
        "log-handler-args = 'a'",
        '',
    ] == basedir.join('buildout.cfg').read().splitlines()
    assert [
        '[install]',
        'eggs_dir = py-eggs',
        '',
        '[admin]',
        'login = me',
        'password = secret',
        '',
        '[server]',
        'host = my.computer.local',
        'port = 13090',
        'username = ',
        '',
        '[log]',
        'handler = FileHandler',
        'max_size = 1000',
        'when = midnight',
        'interval = 1',
        'backups = 5',
        '',
        '[packages]',
        'package_1 = ',
        '',
        '[migration]',
        'do_migration = no',
        'stop_server = no',
        'start_server = no',
        'old_instance = ',
        '',
    ] == basedir.join('install.user.ini').read().splitlines()
    assert [
        '<configure xmlns="http://namespaces.zope.org/zope">',
        '  <principal',
        '    id="icemac.addressbook.global.Administrator"',
        '    title="global administrator"',
        '    login="me"',
        '    password_manager="Plain Text"',
        '    password="secret" />',
        '  <grant',
        '    role="icemac.addressbook.global.Administrator"',
        '    principal="icemac.addressbook.global.Administrator" />',
        '  <grant',
        '    permission="zope.ManageContent"',
        '    principal="icemac.addressbook.global.Administrator" />',
        '</configure>',
    ] == basedir.join('admin.zcml').read().splitlines()
