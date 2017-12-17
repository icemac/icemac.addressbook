(function($) {
    "use strict";

    $("#prefs-category-edit-form fieldset").click(function(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        if ($.inArray(ev.target.nodeName, ["LEGEND", "FIELDSET"]) != -1) {
            var group = $(this).find('div.group');
            $(group).fadeToggle('slow');
        }
    });
})(jQuery);
