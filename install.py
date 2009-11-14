# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import sys
sys.path[0:0] = ['src']

import icemac.addressbook.install
import os.path
import subprocess


if __name__ == '__main__':
    python = sys.executable
    if not icemac.addressbook.install.check_prerequisites():
        sys.exit(-1)
    conf_args = []
    if len(sys.argv) > 1:
        conf_args.append(os.path.join(sys.argv[1], 'install.user.ini'))
    icemac.addressbook.install.Configurator(*conf_args)()

    print 'running %s bootstrap.py ...' % python
    res = subprocess.call([python, 'bootstrap.py'])
    if res:
        sys.exit(res)

    print 'running bin/buildout ...'
    res = subprocess.call(['bin/buildout'])
    if res:
        sys.exit(res)

    print 'Installation complete.'

