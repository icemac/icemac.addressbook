# -*- coding: utf-8 -*-
# Copyright (c) 2011 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.browser.testing import (
    search_for_persons_with_keyword_family_using_browser)

def select_persons_with_keyword_family_for_update(browser=None):
    """Returns a browser where the persons with the keyword `church` are
    selected for the update handler.

    """
    browser = search_for_persons_with_keyword_family_using_browser(browser)
    browser.getControl('Apply on selected persons').displayValue = ['Update']
    browser.getControl(name='form.buttons.apply').click()
    return browser
