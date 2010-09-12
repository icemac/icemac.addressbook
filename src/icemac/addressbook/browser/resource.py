# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

import hurry.resource

css = hurry.resource.Library('css', 'resource')

base_css = hurry.resource.ResourceInclusion(css, 'base.css')
table_css = hurry.resource.ResourceInclusion(css, 'table.css')
form_css = hurry.resource.ResourceInclusion(css, 'form.css')
no_max_content_css = hurry.resource.ResourceInclusion(
    css, 'no_max_content.css', depends=[form_css])
