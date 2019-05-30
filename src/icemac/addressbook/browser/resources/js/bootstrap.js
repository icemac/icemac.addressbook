$(function () {
    $('.archive.person .group.have-md').popover({
        html: true,
        placement: "auto",
        trigger: "hover",
        title: function() {
            return $(this).find('.metadata').attr('aria-label');
        },
        content: function() {
            return $(this).find('.metadata').html();
        }
    });
});
