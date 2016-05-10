# -*- coding: utf-8 -*-
import fanstatic
import js.jquery
import js.jqueryui
import os.path
import zope.viewlet.viewlet


css_lib = fanstatic.Library('css', os.path.join('resources', 'css'))
js_lib = fanstatic.Library('js', os.path.join('resources', 'js'))


# CSS
reset_css = fanstatic.Resource(css_lib, 'reset.css')
base_css = fanstatic.Resource(css_lib, 'base.css', depends=[reset_css])
table_css = fanstatic.Resource(css_lib, 'table.css')
form_css = fanstatic.Resource(css_lib, 'form.css')
wizard_css = fanstatic.Resource(css_lib, 'wizard.css')
prefs_css = fanstatic.Resource(css_lib, 'prefs.css', depends=[form_css])
css = fanstatic.Group([
    base_css,
    form_css,
    prefs_css,
    table_css,
    wizard_css,
])

# not rendered on every page
no_max_content_css = fanstatic.Resource(
    css_lib, 'no_max_content.css', depends=[form_css])
background_css = fanstatic.Resource(
    css_lib, 'background.css', depends=[base_css])


# JavaScript
masterdata_fields = fanstatic.Resource(
    js_lib, 'masterdata_fields.js', bottom=True,
    depends=[js.jqueryui.ui_sortable])
table = fanstatic.Resource(
    js_lib, 'table.js', bottom=True, depends=[js.jquery.jquery])
prefs = fanstatic.Resource(
    js_lib, 'prefs.js', bottom=True, depends=[js.jqueryui.effects_fade])
form = fanstatic.Resource(
    js_lib, 'form.js', bottom=True, depends=[js.jquery.jquery])


js = fanstatic.Group([
    form,
    masterdata_fields,
    prefs,
    table,
])


class DefaultResources(zope.viewlet.viewlet.ViewletBase):
    """Resources which are needed for each page."""

    def update(self):
        css.need()
        js.need()

    def render(self):
        return u''


class AddressBookResources(zope.viewlet.viewlet.ViewletBase):
    """Resources which are address book specific."""

    def update(self):
        background_css.need()

    def render(self):
        return u''
