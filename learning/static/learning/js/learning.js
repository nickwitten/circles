$(document).ready(function() {
    resize_item_info();
});

$(window).resize(function() {
    resize_item_info();
})

function resize_item_info() {
    var height = $('#content').height();
    console.log($(window).width());
    if ($(window).width() > 770) {
        var width = $('#content').width()/2 + 5;
    } else {
        var width = $('#content').width() + 25;
    }
    $("#item-info").height(height);
    $("#item-info").width(width);
}