# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

import hurry.resource
import os.path


css = hurry.resource.Library('css', os.path.join('resources', 'css'))


reset_css = hurry.resource.ResourceInclusion(css, 'reset.css')
base_css = hurry.resource.ResourceInclusion(
    css, 'base.css', depends=[reset_css])
table_css = hurry.resource.ResourceInclusion(css, 'table.css')
form_css = hurry.resource.ResourceInclusion(css, 'form.css')
no_max_content_css = hurry.resource.ResourceInclusion(
    css, 'no_max_content.css', depends=[form_css])
