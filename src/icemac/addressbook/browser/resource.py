# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Michael Howitz
# See also LICENSE.txt

import fanstatic
import js.jquery
import js.jqueryui
import os.path


# CSS
css_lib = fanstatic.Library('css', os.path.join('resources', 'css'))


reset_css = fanstatic.Resource(css_lib, 'reset.css')
base_css = fanstatic.Resource(css_lib, 'base.css', depends=[reset_css])
table_css = fanstatic.Resource(css_lib, 'table.css')
form_css = fanstatic.Resource(css_lib, 'form.css')
no_max_content_css = fanstatic.Resource(
    css_lib, 'no_max_content.css', depends=[form_css])
wizard_css = fanstatic.Resource(css_lib, 'wizard.css')


# JavaScript
js_lib = fanstatic.Library('js', os.path.join('resources', 'js'))

masterdata_fields = fanstatic.Resource(
    js_lib, 'masterdata_fields.js', depends=[js.jqueryui.ui_sortable])

table = fanstatic.Resource(
    js_lib, 'table.js', depends=[js.jquery.jquery])
