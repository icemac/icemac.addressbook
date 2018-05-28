(function($) {
    "use strict";

    $('.checkall').on('click', function() {
        // Check all checkboxes in table body:
        $(this).parents('table').find('tbody :checkbox').prop('checked', this.checked);
    });
})(jQuery);
