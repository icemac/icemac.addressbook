# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import os.path
import shutil
import subprocess
import sys

sys.path[0:0] = ['src']
import icemac.addressbook.install  # noqa: E402
from icemac.addressbook._compat import configparser  # noqa: E402


USER_INI = 'install.user.ini'


def run_process(text, *args):
    """Run a script in a subprocess."""
    print('{} ...'.format(text))
    res = subprocess.call(args)
    if res:
        sys.exit(res)


def bool_get(config, key):
    """Read value from config."""
    value = config.get('migration', key)
    return value == 'yes'


def copy_dir(src_base, dest_base, *path_parts):
    """Copy directory from src_base + path_parts to dest_base + path_parts."""
    path = os.path.join(*path_parts)
    src_dir = os.path.join(src_base, path)
    dest_dir = os.path.join(dest_base, path)
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    shutil.copytree(src_dir, dest_dir)


def delete_dir_contents(*path_parts):
    """Remove the contents of a directory, but keep the directory.

    Currently it is deleted and recreated afterwards.
    """
    path = os.path.join(*path_parts)
    shutil.rmtree(path)
    os.mkdir(path)


def migrate():
    """Migrate an old address book instance."""
    # Read the ini file the configurator just created to get the
    # migration options.
    config = configparser.SafeConfigParser()
    config.read(USER_INI)

    if not bool_get(config, 'do_migration'):
        # no migration wanted
        return
    old_instance = config.get('migration', 'old_instance')
    if not (old_instance and
            os.path.exists(os.path.join(old_instance, USER_INI))):
        print('ERROR: You did not provide a path to the old instance.')
        print('       So I can not migrate the old content.')
        sys.exit(-1)
    cwd = os.getcwd()
    try:
        os.chdir(old_instance)
        demon_path = os.path.join('bin', 'addressbook')
        if bool_get(config, 'stop_server'):
            run_process('Stopping old instance', demon_path, 'stop')
        run_process('Packing the old instance keeping 1 day of old data',
                    os.path.join(cwd, 'bin', 'offlinepack'), '--days=1',
                    os.path.join('var', 'Data.fs'))
        run_process('Creating backup of old instance',
                    os.path.join('bin', 'snapshotbackup'))
        print('Copying data backups to new instance ...')
        copy_dir(old_instance, cwd, 'var', 'snapshotbackups')
        print('Copying blob backups to new instance ...')
        copy_dir(old_instance, cwd, 'var', 'blobstoragesnapshots')
    finally:
        os.chdir(cwd)

    run_process('Restoring backup into new instance',
                os.path.join('bin', 'snapshotrestore'), '--no-prompt')

    # Backups are no longer needed after successful restore:
    delete_dir_contents(cwd, 'var', 'blobstoragesnapshots')
    delete_dir_contents(cwd, 'var', 'snapshotbackups')

    if bool_get(config, 'start_server'):
        run_process('Starting new instance', demon_path, 'start')


if __name__ == '__main__':
    python = sys.executable
    if icemac.addressbook.install.not_matched_prerequisites():
        print(icemac.addressbook.install.not_matched_prerequisites())
        sys.exit(-1)
    conf_args = []
    if len(sys.argv) > 1:
        conf_args.append(os.path.join(sys.argv[1], USER_INI))
    icemac.addressbook.install.Configurator(*conf_args)()

    run_process('running %s bootstrap.py' % python, python, 'bootstrap.py',
                '--setuptools-version=20.3.1', '--buildout-version=2.5.0')
    run_process('running bin/buildout', 'bin/buildout')
    migrate()

    print('Installation complete.')
