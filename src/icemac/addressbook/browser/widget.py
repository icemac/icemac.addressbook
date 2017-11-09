import collections
import z3c.form.browser.select
import z3c.form.interfaces


JAVASCRIPT_TEMPLATE = '''\
$('#{id}').select2({{
  width: '35em'
}});
// ensure order by moving selected items to the bottom of the select tag
// in the order they are selected.
$('#{id}').on('select2:select', function(e){{
      var id = e.params.data.id;
      var option = $(e.target).children('[value='+id+']');
      option.detach();
      $(e.target).append(option).change();
    }});
'''


class Select2ListFieldWidget(z3c.form.browser.select.SelectWidget):
    """Widget for a list field rendered using the select2 JS library."""

    klass = u'select2-ordered-multi-select'
    multiple = 'multiple'

    # def extract(self, default=z3c.form.interfaces.NO_VALUE):
    #     return super(Select2ListFieldWidget, self).extract(default=default)

    @property
    def items(self):
        items = super(Select2ListFieldWidget, self).items
        value_item_map = collections.OrderedDict(
            (x['value'], x) for x in items)
        # Move the selected items to the bottom to keep the order like JS it
        # does:
        not_selected_items = [data
                              for value, data in value_item_map.items()
                              if value not in self.value]
        selected_items = [value_item_map[x]
                          for x in self.value]
        return not_selected_items + selected_items

    def javascript(self):
        """Return JavaScript code for the widget."""
        return JAVASCRIPT_TEMPLATE.format(id=self.id)


def Select2ListChoiceFieldWidgetFactory(context, field, request):
    """Create a Select2ListFieldWidget as field widget.

    This factory is registered for list of choice.
    """
    return z3c.form.widget.FieldWidget(
        context, Select2ListFieldWidget(request))
