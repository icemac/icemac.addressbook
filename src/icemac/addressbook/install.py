# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 Michael Howitz
# See also LICENSE.txt

import os.path
import sys
import ConfigParser


def check_prerequisites():
    "Check whether icemac.addressbook can be installed."
    if os.path.exists('buildout.cfg'):
        print "ERROR: buildout.cfg already exists."
        print "       Please (re-)move the existing one and restart install."
        return False
    if sys.version_info[:2] != (2, 5):
        print "ERROR: icemac.addressbook currently only supports python 2.5,"
        print "       but you try to install it using python %s.%s.%s." % (
            sys.version_info[:3])
        return False
    return True

class Configurator(object):
    """Configure installation.

    user_config ... path to config file with previously entered user values
                    which take precedence over application defaults.
                    Might be None, so no user values are used.
    """

    def __init__(self, user_config=None):
        self.user_config = user_config

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
        except ConfigParser.NoOptionError:
            if global_default is None:
                raise
            else:
                default = global_default
        while True:
            print ' %s: [%s] ' % (question, default),
            got = sys.stdin.readline().strip()
            print
            if not got:
                got = default
            if not values or got in values:
                break
            else:
                print 'ERROR: %r is not in %r.' % (got, values)
                print 'Please choose a value out of the list.'

        self._conf.set(section, option, got)
        return got

    def get(self, section, key):
        return self._conf.get(section, key)

    def load(self):
        """Load the configutation from file.

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
        self._conf = ConfigParser.SafeConfigParser()
        self._conf.read(to_read)
        if self.user_config is not None:
            self._conf.set('migration', 'old_instance',
                           os.path.dirname(self.user_config))
        else:
            self._conf.set('migration', 'old_instance', '')


    def print_intro(self):
        print 'Welcome to icemac.addressbook installation'
        print
        print 'Hint: to use the default value (the one in [brackets]), ',
        print 'enter no value.'
        print

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

    def get_log_options(self):
        print ' Please choose Log-Handler:'
        print '    Details see',
        print 'http://docs.python.org/library/logging.html#handler-objects'
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
        print ' When you need additional packages (e. g. import readers)'
        print ' enter the package names here separated by a newline.'
        print ' When you are done enter an empty line.'
        print ' Known packages:'
        print '   icemac.ab.importer -- Import of CSV files'
        print '   icemac.ab.importxls -- Import of XLS (Excel) files'

    def get_additional_packages(self):
        packages = []
        index = 1
        while True:
            package = self.ask_user(
                'Package %s' % index, 'packages', 'package_%s' % index,
                global_default = '')
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
        print 'The old address book instance must not run during migration.'
        print 'When it runs as demon process the migration script can stop it',
        print 'otherwise you have to stop it manually.'
        self.stop_server = self.ask_user(
            'Old instance is running as a demon process', 'migration',
            'stop_server', values=yes_no)
        self.start_server = self.ask_user(
            'New instance should be started as a demon process after migration',
            'migration', 'start_server', values=yes_no)

    def create_admin_zcml(self):
        print 'creating admin.zcml ...'
        admin_zcml = file('admin.zcml', 'w')
        admin_zcml.write('\n'.join(
                ('<configure xmlns="http://namespaces.zope.org/zope">',
                 '  <principal',
                 '    id="icemac.addressbook.global.Administrator"',
                 '    title="global administrator"',
                 '    login="%s"' % self.admin_login,
                 '    password_manager="Plain Text"',
                 '    password="%s" />' % self.admin_passwd,
                 '  <grant',
                 '    role="zope.Manager"',
                 '    principal="icemac.addressbook.global.Administrator" />',
                 '</configure>',
                 )))
        admin_zcml.close()

    def create_buildout_cfg(self):
        print 'creating buildout.cfg ...'
        buildout_cfg = ConfigParser.SafeConfigParser()
        buildout_cfg.add_section('buildout')
        buildout_cfg.set('buildout', 'extends', 'profiles/prod.cfg')
        buildout_cfg.set('buildout', 'newest', 'true')
        buildout_cfg.set('buildout', 'allow-picked-versions', 'true')
        buildout_cfg.set('buildout', 'eggs-directory', self.eggs_dir)
        buildout_cfg.add_section('deploy.ini')
        buildout_cfg.set('deploy.ini', 'host', self.host)
        buildout_cfg.set('deploy.ini', 'port', self.port)
        log_handler = self.log_handler
        if log_handler == 'FileHandler':
            b_log_handler = log_handler
        else:
            # Argh, all other log handlers live in a subpackage
            b_log_handler = 'handlers.' + log_handler
        buildout_cfg.set('deploy.ini', 'log-handler', b_log_handler)
        if log_handler == 'FileHandler':
            log_args = "'a'"
        elif log_handler == 'RotatingFileHandler':
            log_args = ', '.join(("'a'", self.log_max_bytes, self.log_backups))
        elif log_handler == 'TimedRotatingFileHandler':
            log_when = "'%s'" % self.log_when
            log_args = ', '.join(
                (log_when, self.log_interval, self.log_backups))
        buildout_cfg.set('deploy.ini', 'log-handler-args', log_args)

        if self.packages:
            buildout_cfg.add_section('site.zcml')
            permissions_zcml = (
                '<include package="' +
                '" />\n<include package="'.join(self.packages) +
                '" />')
            buildout_cfg.set('site.zcml', 'permissions_zcml', permissions_zcml)

        buildout_cfg_file = file('buildout.cfg', 'w')
        buildout_cfg.write(buildout_cfg_file)
        if self.packages:
            # ConfigParser can't write '+=' instead of '='
            eggs = 'eggs += %s\n\n' % '\n      '.join(self.packages)
            buildout_cfg_file.write('[app]\n')
            buildout_cfg_file.write(eggs)
            buildout_cfg_file.write('[test]\n')
            buildout_cfg_file.write(eggs)

        buildout_cfg_file.close()

    def store(self):
        print 'saving config ...'
        user_conf = file('install.user.ini', 'w')
        self._conf.write(user_conf)
