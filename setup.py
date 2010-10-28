# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt

import os.path
import setuptools

def read(*path_elements):
    return "\n\n" + file(os.path.join(*path_elements)).read()

version = '1.5.0dev'

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
        'Development Status :: 4 - Beta',
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
        'StableDict',
        'ZConfig',
        'ZODB3',
        'classproperty',
        'gocept.country',
        'gocept.pagelet',
        'gocept.reference',
        'hurry.jquery',
        'hurry.resource',
        'hurry.zoperesource',
        'icemac.ab.locales [compile] >= 0.5',
        'icemac.truncatetext',
        'setuptools',
        'xlwt',
        'z3c.authviewlet',
        'z3c.flashmessage',
        'z3c.form >= 2.2.0dev',
        'z3c.formui',
        'z3c.layer.pagelet',
        'z3c.locales [compile] >= 0.3.0',
        'z3c.menu.ready2go',
        'z3c.pagelet',
        'z3c.preference',
        'z3c.ptcompat',
        'z3c.table',
        'zc.catalog',
        'zc.sourcefactory',
        'zdaemon',
        'zope.app.appsetup',
        'zope.app.debug',
        'zope.app.locales >= 3.6.0',
        'zope.app.principalannotation',
        'zope.app.wsgi',
        'zope.browserpage',
        'zope.copypastemove',
        'zope.generations',
        'zope.globalrequest',
        'zope.i18n [zcml,compile]',
        'zope.interface',
        'zope.login',
        'zope.mimetype',
        'zope.pluggableauth',
        'zope.preference',
        'zope.principalregistry',
        'zope.publisher',
        'zope.securitypolicy',
        'zope.session',
        'zope.traversing',
        'zope.app.authentication', # XXX required by older installations,
                                   # deprecated and converted in 1.5
                                   # (evolve3.py), remove in version 1.7 (Add
                                   # notice to CHANGES.txt then, to show what
                                   # to do to upgrade when evolve to
                                   # generation 16 fails.)
        'zope.app.form', # XXX needed by zope.mimetype 1.3.0
        ],
    extras_require = dict(
        test=[
            'xlrd',
            'z3c.etestbrowser',
            'zc.buildout',
            'zope.testbrowser',
            'zope.testing',
            ],
        z3cpt=[
            'z3c.pt',
            ],
        ),
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
