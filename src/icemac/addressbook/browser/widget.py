# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

import z3c.form.browser.orderedselect
import z3c.form.widget


def sort_key(value):
    "Sort key for widget."
    return value['content'].lower()


class SortedSelectWidget(z3c.form.browser.orderedselect.OrderedSelectWidget):
    "OrderedSelectWidget which sorts the selected values itself."

    def update(self):
        super(SortedSelectWidget, self).update()
        self.selectedItems = sorted(self.selectedItems, key=sort_key)
        self.notselectedItems = sorted(self.notselectedItems, key=sort_key)

def SortedSelectFieldWidget(field, request):
    """IFieldWidget factory for SortedSelectWidget."""
    return z3c.form.widget.FieldWidget(field, SortedSelectWidget(request))
