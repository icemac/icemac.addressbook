# -*- coding: utf-8 -*-
# Copyright (c) 2009 Michael Howitz
# See also LICENSE.txt

import zope.viewlet.viewlet
import z3c.template.template


class Viewlet(zope.viewlet.viewlet.ViewletBase):
    "Master data viewlet."
    # We need a viewlet class here, so other packages may register
    # masterdata viewlets without duplicating the template.

    def render(self):
        return z3c.template.template.getPageTemplate()(self)
