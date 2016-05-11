(function($) {

    function render_field_hint(index, widget) {
        /* Render the title attribute of a form field as hint.

        widget ... z3c.form widget rendered in browser.
        */
        widget = $(widget);
        var text = widget.find('input, select').attr('title');
        if (!text) {
            return;
        }
        widget.append('<div class="hint">' + text + '</div>');
    }

    // Put focus on first input field of form:
    $("form div.widget:first input").focus();
    // Render field descriptions as hints.
    $.each($('form .widget'), render_field_hint);

})(jQuery);
