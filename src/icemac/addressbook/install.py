# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import os.path
import sys
import ConfigParser


def ask_user(conf, question, section, option):
    "Ask the user for a value of section/option and store it in config."
    default = conf.get(section, option)
    print ' %s: [%s] ' % (question, default),
    got = sys.stdin.readline().strip()
    print
    if not got:
        got = default
    conf.set(section, option, got)
    return got


def check_prerequisites():
    "Check whether icemac.addressbook can be installed."
    if os.path.exists('buildout.cfg'):
        print "ERROR: buildout.cfg already exists."
        print "       Please move the existing one and restart install."
        return False
    if sys.version_info[:2] != (2, 5):
        print "ERROR: icemac.addressbook currently only supports python 2.5,"
        print "       but you try to install it using python %s.%s.%s." % (
            sys.version_info[:3])
        return False
    return True


def config(user_config=None):
    """Configure installation.

    user_config ... path to config file with previously entered user values
                    which take precedence over application defaults.
                    Might be None, so no user values are used.
    """
    if user_config is not None and not os.path.exists(user_config):
        raise IOError('%r does not exist.' % user_config)

    to_read = ['install.default.ini']
    if user_config is not None:
        to_read.append(user_config)

    # create config
    conf = ConfigParser.SafeConfigParser()
    conf.read(to_read)

    # introduction
    print 'Welcome to icemac.addressbook installation'
    print
    print 'Hint: to use the default value (the one in [brackets]), enter no',
    print 'value.'
    print

    # ask user some questions
    eggs_dir = ask_user(
        conf, 'Directory to store python eggs', 'install', 'eggs_dir')
    admin_login = ask_user(
        conf, 'Log-in name for the administrator', 'admin', 'login')
    admin_passwd = ask_user(
        conf, 'Password for the administrator', 'admin', 'password')
    host = ask_user(conf, 'Hostname', 'server', 'host')
    port = ask_user(conf, 'Port number', 'server', 'port')
    print ' Please choose Log-Handler:'
    print '    Details see',
    print 'http://docs.python.org/library/logging.html#handler-objects'
    handlers = (
        'FileHandler', 'RotatingFileHandler', 'TimedRotatingFileHandler')
    log_handler = None
    while log_handler not in handlers:
        log_handler = ask_user(
            conf, 'Log-Handler, choose between ' + ', '.join(handlers), 'log',
            'handler')
        if log_handler not in handlers:
            print 'ERROR: %r is not in %r.' % (log_handler, handlers)
            print 'Please choose one handler out of the list.'
    if log_handler == 'RotatingFileHandler':
        log_max_bytes = ask_user(
            conf, 'Maximum file size before rotating in bytes', 'log',
            'max_size')
    elif log_handler == 'TimedRotatingFileHandler':
        log_when = ask_user(
            conf,
            'Type of rotation interval, choose between S, M, H, D, W, midnight',
            'log', 'when')
        log_interval = ask_user(
            conf, 'Rotation interval size', 'log', 'interval')
    if log_handler in ('RotatingFileHandler', 'TimedRotatingFileHandler'):
        log_backups = ask_user(
            conf, 'Number of log file backups', 'log', 'backups')

    # create admin.zcml
    print 'creating admin.zcml ...'
    admin_zcml = file('admin.zcml', 'w')
    admin_zcml.write('\n'.join(
            ('<configure xmlns="http://namespaces.zope.org/zope">',
             '  <principal',
             '    id="icemac.addressbook.global.Administrator"',
             '    title="global administrator"',
             '    login="%s"' % admin_login,
             '    password_manager="Plain Text"',
             '    password="%s" />' % admin_passwd,
             '  <grant',
             '    role="zope.Manager"',
             '    principal="icemac.addressbook.global.Administrator" />',
             '</configure>',
             )))
    admin_zcml.close()

    # create buildout.cfg
    print 'creating buildout.cfg ...'
    buildout_cfg = ConfigParser.SafeConfigParser()
    buildout_cfg.add_section('buildout')
    buildout_cfg.set('buildout', 'extends', 'profiles/prod.cfg')
    buildout_cfg.set('buildout', 'eggs-directory', eggs_dir)
    buildout_cfg.add_section('deploy.ini')
    buildout_cfg.set('deploy.ini', 'host', host)
    buildout_cfg.set('deploy.ini', 'port', port)
    if log_handler == 'FileHandler':
        b_log_handler = log_handler
    else:
        # Argh, all other log handlers live in a subpackage
        b_log_handler = 'handlers.' + log_handler
    buildout_cfg.set('deploy.ini', 'log-handler', b_log_handler)
    if log_handler == 'FileHandler':
        log_args = "'a'"
    elif log_handler == 'RotatingFileHandler':
        log_args = ', '.join(("'a'", log_max_bytes, log_backups))
    elif log_handler == 'TimedRotatingFileHandler':
        log_when = "'%s'" % log_when
        log_args = ', '.join((log_when, log_interval, log_backups))
    buildout_cfg.set('deploy.ini', 'log-handler-args', log_args)
    buildout_cfg_file = file('buildout.cfg', 'w')
    buildout_cfg.write(buildout_cfg_file)
    buildout_cfg_file.close()

    # save confing
    print 'saving config ...'
    user_conf = file('install.user.ini', 'w')
    conf.write(user_conf)
