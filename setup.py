# -*- coding: utf-8 -*-
import setuptools


def read(filename):
    """Read a file in the current directory."""
    with open(filename) as f:
        return f.read()


version = '9.3'


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
    download_url='https://pypi.org/project/icemac.addressbook',
    url='https://github.com/icemac/icemac.addressbook',
    project_urls={
        'Documentation': 'https://icemacaddressbook.readthedocs.io',
        'Source': 'https://github.com/icemac/icemac.addressbook',
        'Tracker': 'https://github.com/icemac/icemac.addressbook/issues',
    },
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Paste',
        'Framework :: Zope :: 3',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Natural Language :: German',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Communications :: Email :: Address Book',
        'Topic :: Communications :: Telephony',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Office/Business :: Groupware',
    ],
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['icemac'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'ZConfig',
        'ZODB',
        'fanstatic',
        'gocept.country',
        'gocept.pagelet',
        'gocept.reference',
        'grokcore.component >= 2.5.1.dev1',
        'icalendar',
        'icemac.ab.locales [compile] >= 2.24',
        'icemac.truncatetext',
        'js.bootstrap4',
        'js.cookieconsent',
        'js.jquery',
        'js.jquery_timepicker_addon',
        'js.jqueryui',
        'js.select2',
        'setuptools',
        'six',
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
        'z3c.table >= 2',
        'z3c.wizard',
        'zc.catalog',
        'zc.sourcefactory',
        'zdaemon',
        'zodbupdate',
        'zope.schema >= 4.3'
        'zope.app.appsetup',
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
        'zope.securitypolicy >= 4.1',
        'zope.session',
        'zope.traversing',
    ],
    extras_require=dict(
        test=[
            'WebTest >= 2.0.25.dev0',
            'beautifulsoup4',
            'gocept.httpserverlayer',
            'gocept.jslint',
            'gocept.testing',
            'mock',
            'plone.testing',
            'pytest',
            'selenium >= 3',
            'xlrd',
            'z3c.etestbrowser',
            'zc.buildout',
            'zope.testbrowser >= 5.2.3.dev0',
            'zope.testing >= 3.8',
        ],
        docs=[
            'Sphinx',
            'recommonmark',
        ]
    ),
    entry_points="""
      [console_scripts]
      debug = icemac.addressbook.startup:interactive_debug_prompt
      [paste.app_factory]
      main = icemac.addressbook.startup:application_factory
      [fanstatic.libraries]
      css = icemac.addressbook.browser.resource:css_lib
      js = icemac.addressbook.browser.resource:js_lib
      """
)
