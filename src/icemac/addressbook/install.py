from __future__ import absolute_import, print_function
import collections
import os.path
import sys
# We cannot depend here on something besides the standard library and this
# compat module as we are the installer of the dependencies!
from icemac.addressbook._compat import configparser


INDEX_URL = "https://pypi.python.org/simple"


def not_matched_prerequisites():
    """Check whether icemac.addressbook can be installed."""
    if os.path.exists('buildout.cfg'):
        return (
            "ERROR: buildout.cfg already exists.\n"
            "       Please (re-)move the existing one and restart install.")
    if sys.version_info[:2] != (2, 7):
        return ("ERROR: icemac.addressbook currently supports only Python 2.7."
                "\n       But you try to install it using Python %s.%s.%s." % (
                    sys.version_info[:3]))
    return False


class Configurator(object):
    """Configure installation.

    user_config ... path to config file with previously entered user values
                    which take precedence over application defaults.
                    Might be None, so no user values are used.
    """

    def __init__(self, user_config=None, stdin=None):
        self.user_config = user_config
        if stdin is not None:
            self.stdin = stdin
        else:
            self.stdin = sys.stdin

    def __call__(self):
        self.load()
        self.print_intro()
        self.get_global_options()
        self.get_server_options()
        self.get_log_options()
        self.print_additional_packages_intro()
        self.get_additional_packages()
        self.get_migration_options()
        self.create_admin_zcml()
        self.create_buildout_cfg()
        self.store()

    def ask_user(
            self, question, section, option, global_default=None, values=()):
        """Ask the user for a value of section/option and store it in config.

        global_default ... use this value as default value when it is not
                           defined in the global config file
        values ... when set, only this value can be entered
        """
        try:
            default = self.get(section, option)
        except configparser.NoOptionError:
            assert global_default is not None
            default = global_default
        while True:
            print(' {question}: [{default}] '.format(
                question=question, default=default), end='')
            got = self.stdin.readline().strip()
            print()
            if not got:
                got = default
            if not values or got in values:
                break
            else:
                print('ERROR: %r is not in %r.' % (got, values))
                print('Please choose a value out of the list.')

        self._conf.set(section, option, got)
        return got

    def get(self, section, key):
        return self._conf.get(section, key)

    def load(self):
        """Load the configuration from file.

        Default configuration is always read and user configuration is
        read when `user_config` is set on instance.

        """
        if (self.user_config is not None and
                not os.path.exists(self.user_config)):
            raise IOError('%r does not exist.' % self.user_config)

        to_read = ['install.default.ini']
        if self.user_config is not None:
            to_read.append(self.user_config)

        # create config
        self._conf = configparser.SafeConfigParser(
            dict_type=collections.OrderedDict)
        self._conf.read(to_read)
        if self.user_config is not None:
            self._conf.set('migration', 'old_instance',
                           os.path.dirname(self.user_config))
        else:
            self._conf.set('migration', 'old_instance', '')

    def print_intro(self):
        print('Welcome to icemac.addressbook installation')
        print()
        print('Hint: to use the default value (the one in [brackets]), '
              'enter no value.')
        print()

    def get_global_options(self):
        self.eggs_dir = self.ask_user(
            'Directory to store python eggs', 'install', 'eggs_dir')

    def get_server_options(self):
        self.admin_login = self.ask_user(
            'Log-in name for the administrator', 'admin', 'login')
        self.admin_passwd = self.ask_user(
            'Password for the administrator', 'admin', 'password')
        self.host = self.ask_user('Hostname', 'server', 'host')
        self.port = self.ask_user('Port number', 'server', 'port')
        self.username = self.ask_user(
            'Username whether process should run as different user otherwise '
            'emtpy', 'server', 'username')

    def get_log_options(self):
        print(' Please choose Log-Handler:')
        print('    Details see '
              'http://docs.python.org/library/logging.html#handler-objects')
        handlers = (
            'FileHandler', 'RotatingFileHandler', 'TimedRotatingFileHandler')
        log_handler = None
        log_handler = self.ask_user(
            'Log-Handler, choose between ' + ', '.join(handlers),
            'log', 'handler', values=handlers)
        if log_handler == 'RotatingFileHandler':
            self.log_max_bytes = self.ask_user(
                'Maximum file size before rotating in bytes',
                'log', 'max_size')
        elif log_handler == 'TimedRotatingFileHandler':
            self.log_when = self.ask_user(
                'Type of rotation interval, choose between S, M, H, D, W, '
                'midnight', 'log', 'when',
                values=('S', 'M', 'H', 'D', 'W', 'midnight'))
            self.log_interval = self.ask_user(
                'Rotation interval size', 'log', 'interval')
        if log_handler in ('RotatingFileHandler', 'TimedRotatingFileHandler'):
            self.log_backups = self.ask_user(
                'Number of log file backups', 'log', 'backups')
        self.log_handler = log_handler

    def print_additional_packages_intro(self):
        print(' When you need additional packages (e. g. import readers)')
        print(' enter the package names here separated by a newline.')
        print(' When you are done enter an empty line.')
        print(' Known packages:')
        print('   icemac.ab.importer -- Import of CSV files')
        print('   icemac.ab.importxls -- Import of XLS (Excel) files')
        print(
            '   icemac.ab.calendar -- Calendar using persons in address book')

    def get_additional_packages(self):
        packages = []
        index = 1
        while True:
            package = self.ask_user(
                'Package %s' % index, 'packages', 'package_%s' % index,
                global_default='')
            index += 1
            if not package:
                break
            packages.append(package)
        self.packages = packages

    def get_migration_options(self):
        yes_no = ('yes', 'no')
        self.do_migration = self.ask_user(
            ' Migrate old address book content to new instance', 'migration',
            'do_migration', values=yes_no)
        if self.do_migration == 'no':
            return
        print('The old address book instance must not run during migration.')
        print('When it runs as demon process the migration script can stop it '
              'otherwise you have to stop it manually.')
        self.stop_server = self.ask_user(
            'Old instance is running as a demon process', 'migration',
            'stop_server', values=yes_no)
        self.start_server = self.ask_user(
            'New instance should be started as a demon process after '
            'migration', 'migration', 'start_server', values=yes_no)

    def create_admin_zcml(self):
        print('creating admin.zcml ...')
        with open('admin.zcml', 'w') as admin_zcml:
            admin_zcml.write('\n'.join(
                ('<configure xmlns="http://namespaces.zope.org/zope">',
                 '  <principal',
                 '    id="icemac.addressbook.global.Administrator"',
                 '    title="global administrator"',
                 '    login="%s"' % self.admin_login,
                 '    password_manager="Plain Text"',
                 '    password="%s" />' % self.admin_passwd,
                 '  <grant',
                 '    role="icemac.addressbook.global.Administrator"',
                 '    principal="icemac.addressbook.global.Administrator" />',
                 '  <grant',
                 '    permission="zope.ManageContent"',
                 '    principal="icemac.addressbook.global.Administrator" />',
                 '</configure>',
                 )))

    def create_buildout_cfg(self):
        print('creating buildout.cfg ...')
        buildout_cfg = configparser.SafeConfigParser(
            dict_type=collections.OrderedDict)
        buildout_cfg.add_section('buildout')
        buildout_cfg.set('buildout', 'extends', 'profiles/prod.cfg')
        buildout_cfg.set('buildout', 'newest', 'true')
        buildout_cfg.set('buildout', 'allow-picked-versions', 'true')
        buildout_cfg.set('buildout', 'eggs-directory', self.eggs_dir)
        buildout_cfg.set('buildout', 'index', INDEX_URL)
        buildout_cfg.add_section('deploy.ini')
        buildout_cfg.set('deploy.ini', 'host', self.host)
        buildout_cfg.set('deploy.ini', 'port', self.port)
        if self.username:
            buildout_cfg.add_section('zdaemon.conf')
            buildout_cfg.set('zdaemon.conf', 'user', 'user %s' % self.username)
        log_handler = self.log_handler
        if log_handler == 'FileHandler':
            b_log_handler = log_handler
        else:
            # Argh, all other log handlers live in a subpackage
            b_log_handler = 'handlers.' + log_handler
        buildout_cfg.set('deploy.ini', 'log-handler', b_log_handler)
        log_args = getattr(self, '_log_args_{}'.format(log_handler))
        buildout_cfg.set('deploy.ini', 'log-handler-args', log_args)

        if self.packages:
            buildout_cfg.add_section('site.zcml')
            permissions_zcml = (
                '<include package="' +
                '" />\n<include package="'.join(self.packages) +
                '" />')
            buildout_cfg.set('site.zcml', 'permissions_zcml', permissions_zcml)

        with open('buildout.cfg', 'w') as buildout_cfg_file:
            buildout_cfg.write(buildout_cfg_file)
            if self.packages:
                # configparser can't write '+=' instead of '='
                eggs = 'eggs += %s\n\n' % '\n      '.join(self.packages)
                buildout_cfg_file.write('[app]\n')
                buildout_cfg_file.write(eggs)
                buildout_cfg_file.write('[test]\n')
                buildout_cfg_file.write(eggs)

    def store(self):
        print('saving config ...')
        with open('install.user.ini', 'w') as user_conf:
            self._conf.write(user_conf)

    @property
    def _log_args_FileHandler(self):
        return "'a'"

    @property
    def _log_args_RotatingFileHandler(self):
        return ', '.join(("'a'", self.log_max_bytes, self.log_backups))

    @property
    def _log_args_TimedRotatingFileHandler(self):
        log_when = "'%s'" % self.log_when
        return ', '.join((log_when, self.log_interval, self.log_backups))
