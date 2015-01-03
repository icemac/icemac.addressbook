import gocept.jslint
import os


class JSLintTest(gocept.jslint.TestCase):

    jshint_command = os.environ.get('JSHINT_COMMAND', '/bin/true')

    options = (gocept.jslint.TestCase.options +
               ('evil',
                'eqnull',
                'multistr',
                'sub',
                'undef',
                'browser',
                'jquery',
                'devel'
                ))

    include = (
        'icemac.addressbook.browser:resources/js',
    )
