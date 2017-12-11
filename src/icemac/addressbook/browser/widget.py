import collections
import z3c.form.browser.select
import z3c.form.interfaces


# The used JS functions on `document` are defined in ../resources/js/form.js
JAVASCRIPT_TEMPLATE = '''\
$(document).ready(function(){
    $('#%(id)s').select2({
        width: '35em'
    });
    // handle ordering at select and make element sortable:
    $('#%(id)s').on('select2:select',
                    document.select2__keep_selected_items_ordered);
    document.select2__make_selected_items_sortable($('#%(id)s'));
});
'''


class Select2ListFieldWidget(z3c.form.browser.select.SelectWidget):
    """Widget for a list field rendered using the select2 JS library."""

    klass = u'select2-ordered-multi-select'
    multiple = 'multiple'

    @property
    def items(self):
        items = super(Select2ListFieldWidget, self).items
        value_item_map = collections.OrderedDict(
            (x['value'], x) for x in items)
        # Move the selected items to the top to keep the order like JS does it:
        not_selected_items = [data
                              for value, data in value_item_map.items()
                              if value not in self.value]
        selected_items = [value_item_map[x]
                          for x in self.value]
        return selected_items + not_selected_items

    def javascript(self):
        """Return JavaScript code for the widget."""
        return JAVASCRIPT_TEMPLATE % {'id': self.id}


def Select2ListChoiceFieldWidgetFactory(context, field, request):
    """Create a Select2ListFieldWidget as field widget.

    This factory is registered for list of choice.
    """
    return z3c.form.widget.FieldWidget(
        context, Select2ListFieldWidget(request))
