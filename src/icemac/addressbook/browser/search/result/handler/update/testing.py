# -*- coding: utf-8 -*-
# Copyright (c) 2011 Michael Howitz
# See also LICENSE.txt

from icemac.addressbook.browser.testing import (
    search_for_persons_with_keyword_search_using_browser)

def select_persons_with_keyword_for_update(keyword):
    """Returns a browser where the persons with the given keyword are
    selected for the update handler.

    """
    browser = search_for_persons_with_keyword_search_using_browser(keyword)
    browser.getControl('Apply on selected persons').displayValue = ['Update']
    browser.getControl(name='form.buttons.apply').click()
    return browser
