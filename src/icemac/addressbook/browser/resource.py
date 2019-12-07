# -*- coding: utf-8 -*-
import fanstatic
import js.bootstrap4
import js.jquery
import js.jqueryui
import js.select2
import os.path
import zope.viewlet.viewlet


css_lib = fanstatic.Library('css', os.path.join('resources', 'css'))
js_lib = fanstatic.Library('js', os.path.join('resources', 'js'))


# CSS
reset_css = fanstatic.Resource(css_lib, 'reset.css')
hamburger_fold_out_menu_css = fanstatic.Resource(
    css_lib, 'pure-css-hamburger-fold-out-menu.css')
base_css = fanstatic.Resource(css_lib, 'base.css', depends=[
    reset_css, hamburger_fold_out_menu_css])
print_css = fanstatic.Resource(css_lib, 'print.css', depends=[base_css])
table_css = fanstatic.Resource(css_lib, 'table.css')
form_css = fanstatic.Resource(css_lib, 'form.css')
wizard_css = fanstatic.Resource(css_lib, 'wizard.css')
prefs_css = fanstatic.Resource(css_lib, 'prefs.css', depends=[form_css])
css = fanstatic.Group([
    base_css,
    print_css,
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
bootstrap_css = fanstatic.Resource(
    css_lib, 'bootstrap.css', depends=[
        base_css,
        no_max_content_css,
        js.bootstrap4.bootstrap,
    ])


# JavaScript
masterdata_fields = fanstatic.Resource(
    js_lib, 'masterdata_fields.js', bottom=True,
    depends=[js.jqueryui.ui_sortable])
table = fanstatic.Resource(
    js_lib, 'table.js', bottom=True, depends=[js.jquery.jquery])
prefs = fanstatic.Resource(
    js_lib, 'prefs.js', bottom=True, depends=[js.jqueryui.effects_fade])
form = fanstatic.Resource(
    js_lib, 'form.js', bottom=True,
    depends=[js.jquery.jquery, js.select2.select2])
bootstrap_js = fanstatic.Resource(
    js_lib, 'bootstrap.js', bottom=True,
    depends=[js.bootstrap4.bootstrap])


js_group = fanstatic.Group([
    form,
    masterdata_fields,
    prefs,
    table,
])
bootstrap = fanstatic.Group([
    bootstrap_css,
    bootstrap_js,
])


class DefaultResources(zope.viewlet.viewlet.ViewletBase):
    """Resources which are needed for each page."""

    def update(self):
        css.need()
        js_group.need()
        lang = self.request.locale.id.language
        if not lang:
            lang = 'en'
        # Besides that need select2 expects that a lang attribute is set on any
        # HTML container of the select element.
        js.select2.locales[lang].need()

    def render(self):
        return u''


class AddressBookResources(zope.viewlet.viewlet.ViewletBase):
    """Resources which are address book specific."""

    def update(self):
        background_css.need()

    def render(self):
        return u''
