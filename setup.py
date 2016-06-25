# -*- coding: utf-8 -*-
import setuptools


def read(filename):
    """Read a file in the current directory."""
    return file(filename).read()


version = '2.7'


setuptools.setup(
    name='icemac.addressbook',
    version=version,
    description="Multi user address book application",
    long_description="\n\n".join([
        read('README.rst'),
        read('HACKING.rst'),
        read('CHANGES.rst')]
    ),
    keywords='python address book addressbook zope3 zope application web '
             'phone number e-mail email home page homepage wsgi',
    author='Michael Howitz',
    author_email='icemac@gmx.net',
    download_url='http://pypi.python.org/pypi/icemac.addressbook',
    url='https://bitbucket.org/icemac/icemac.addressbook',
    license='ZPL 2.1',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
        'Natural Language :: German',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
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
    package_dir={'': 'src'},
    namespace_packages=['icemac'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'ZConfig',
        'ZODB3',
        'fanstatic',
        'gocept.country',
        'gocept.pagelet',
        'gocept.reference',
        'grokcore.component >= 2.5.1.dev1',
        'icalendar',
        'icemac.ab.locales [compile] >= 2.9',
        'icemac.truncatetext',
        'js.jquery',
        'js.jquery_timepicker_addon',
        'js.jqueryui',
        'setuptools',
        'xlwt',
        'z3c.authviewlet',
        'z3c.flashmessage',
        'z3c.form >= 3.3.1.dev0',
        'z3c.formui',
        'z3c.layer.pagelet',
        'z3c.locales [compile] >= 0.3.0',
        'z3c.menu.ready2go',
        'z3c.pagelet',
        'z3c.pagelet[chameleon]',
        'z3c.preference >= 0.2',
        'z3c.ptcompat',
        'z3c.table',
        'z3c.wizard',
        'zc.catalog',
        'zc.sourcefactory',
        'zdaemon',
        'zodbupdate',
        'zope.schema >= 4.3'
        'zope.app.appsetup',
        'zope.app.debug',
        'zope.app.locales >= 3.6',
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
        'zope.principalannotation',
        'zope.principalregistry',
        'zope.publisher',
        'zope.securitypolicy',
        'zope.session',
        'zope.traversing',
    ],
    extras_require=dict(
        test=[
            'gocept.selenium >= 2.5',
            'gocept.testing',
            'mock',
            'gocept.jslint',
            'plone.testing',
            'xlrd',
            'z3c.etestbrowser',
            'zc.buildout',
            'zope.testbrowser[wsgi]>=4.0',
            'zope.testing >= 3.8',
        ],
    ),
    entry_points="""
      [console_scripts]
      debug = icemac.addressbook.startup:interactive_debug_prompt
      addressbook = icemac.addressbook.startup:zdaemon_controller
      debug_ajax = icemac.addressbook.startup:zdaemon_controller_debug_ajax
      debug_pdb = icemac.addressbook.startup:zdaemon_controller_debug_pdb
      [paste.app_factory]
      main = icemac.addressbook.startup:application_factory
      [fanstatic.libraries]
      css = icemac.addressbook.browser.resource:css_lib
      js = icemac.addressbook.browser.resource:js_lib
      """
)
