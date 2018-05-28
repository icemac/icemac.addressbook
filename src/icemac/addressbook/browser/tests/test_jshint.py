import icemac.addressbook.testing


class JSLintTest(icemac.addressbook.testing.JSLintTest):

    include = (
        'icemac.addressbook.browser:resources/js',
    )
