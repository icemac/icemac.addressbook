# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Michael Howitz
# See also LICENSE.txt

import os.path
import setuptools

def read(*path_elements):
    return "\n\n" + file(os.path.join(*path_elements)).read()

version = '0.5.2'

setuptools.setup(
    name='icemac.addressbook',
    version=version,
    description="Multi user address book application",
    long_description=(
        read('README.txt') +
        read('INSTALL.txt') +
        read('TODO.txt') +
        read('CHANGES.txt')
        ),
    keywords='python address book addressbook zope3 zope application web '
             'phone number e-mail email home page homepage',
    author='Michael Howitz',
    author_email='icemac@gmx.net',
    url='http://pypi.python.org/pypi/icemac.addressbook',
    license='ZPL 2.1',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Paste',
        'Framework :: Zope3',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Religion',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved',
        'License :: OSI Approved :: Zope Public License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Topic :: Communications',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Address Book',
        'Topic :: Communications :: Telephony',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Groupware',
        'Topic :: Religion',
        ],
    packages=setuptools.find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['icemac'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.interface',
        'ZODB3',
        'ZConfig',
        'zdaemon',
        'zope.publisher',
        'zope.traversing',
        'zope.app.wsgi',
        'zope.app.appsetup',
        'zope.app.authentication',
        'zope.session',
        'zope.i18n',
        'zope.app.principalannotation',
        # Packages required by application
        'zc.sourcefactory',
        'zope.securitypolicy',
        'zope.app.generations',
        'z3c.form >= 2.2.0dev',
        'z3c.formui',
        'z3c.layer.pagelet',
        'z3c.pagelet',
        'z3c.ptcompat',
        'gocept.reference',
        'StableDict',
        'gocept.country',
        'gocept.pagelet',
        'z3c.menu.ready2go',
        'zc.catalog',
        'xlwt',
        'z3c.table',
        'classproperty',
        'icemac.truncatetext',
        'z3c.pt',
        'zope.app.debug',
        'zope.mimetype',
        'zope.app.intid',  # XXX required by older installations,
                           # deprecated and converted in 0.3
                           # (evolve3.py), remove in version 0.6 (Add
                           # notice to CHANGES.txt then, to show what
                           # to do to upgrade when evolve to
                           # generation 3 fails.)
        'zope.app.catalog',# XXX required by older installations,
                           # deprecated and converted in 0.3
                           # (evolve3.py), remove in version 0.6 (Add
                           # notice to CHANGES.txt then, to show what
                           # to do to upgrade when evolve to
                           # generation 3 fails.)
        'zope.app.folder', # XXX required by older installations,
                           # deprecated and converted in 0.3
                           # (evolve4.py), remove in version 0.6 (Add
                           # notice to CHANGES.txt then, to show what
                           # to do to upgrade when evolve to
                           # generation 4 fails.)
        ],
    extras_require = dict(
        test=[
            'xlrd',
            'zc.buildout',
            'zope.app.testing',
            'zope.testbrowser',
            'zope.testing',
            ]),
    entry_points = """
      [console_scripts]
      debug = icemac.addressbook.startup:interactive_debug_prompt
      addressbook = icemac.addressbook.startup:zdaemon_controller
      debug_ajax = icemac.addressbook.startup:zdaemon_controller_debug_ajax
      debug_pdb = icemac.addressbook.startup:zdaemon_controller_debug_pdb
      [paste.app_factory]
      main = icemac.addressbook.startup:application_factory
      """
    )
