(function($) {
    "use strict";

    function render_field_hint(index, widget) {
        /* Render the title attribute of a form field as hint.

        widget ... z3c.form widget rendered in browser.
        */
        widget = $(widget);
        var text = widget.find('input, select').attr('title');
        if (!text) {
            return;
        }
        widget.append('<div class="hint no-print">' + text + '</div>');
    }

    // Put focus on first input field of form:
    $("form div.widget:first input").focus();
    // Render field descriptions as hints.
    $.each($('form .widget'), render_field_hint);
    $('form select.set-field, \
       form select.tuple-field, \
       form select.choice-field').select2({
        width: "35em",
        minimumResultsForSearch: 7
    });


    function _select2_order_options($select2) {
        var ul = $select2.next('.select2-container').first('ul.select2-selection__rendered');
        $($(ul).find('.select2-selection__choice').get().reverse()).each(function() {
            var id = $(this).data('data').id;
            var option = $select2.find('option[value="' + id + '"]')[0];
            $select2.prepend(option);
        });
    }

    document.select2__keep_selected_items_ordered = function(e) {
        /* Handle a select2 select event to keep the order.

        Usage: $('#<id>').on('select2:select',
                             document.select2__keep_selected_items_ordered);
         */
        _select2_order_options($(e.target));
    };

    document.select2__make_selected_items_sortable = function($select2) {
        /* Make a select 2 field sortable.

        Usage: document.select2__make_selected_items_sortable($('#<id>'));
        */
        var ul = $select2.next('.select2-container').first('ul.select2-selection__rendered');
        ul.sortable({
            placeholder: 'ui-state-highlight',
            forcePlaceholderSize: true,
            items: 'li:not(.select2-search__field)',
            tolerance: 'pointer',
            stop: function() {_select2_order_options($select2);}
        });
    };
})(jQuery);
