(function($) {
    "use strict";

    // Return a helper with preserved width of cells
    var fixHelper = function(e, ui) {
	    ui.children().each(function() {
		    $(this).width($(this).width());
	    });
	    return ui;
    };

    $("table#entity-fields tbody").sortable({
        helper: fixHelper,
        axis: "y",
        cursor: 'row-resize'
    }).disableSelection();

    $("button#entity-fields-save").click(function() {
        var fields_array = $("table#entity-fields tbody").sortable('toArray');
        var query = '?f:list=' + fields_array.join('&f:list=');
        var submit_url = window.location.href + '/@@save-sortorder.html'+ query;
        window.location.href = submit_url;
    });
})(jQuery);
