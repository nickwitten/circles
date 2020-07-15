function show_update_info() {
    $(this).closest('item-info').find('update').show();
    $(this).hide();
}

function format_site_select_data() {
    var site_select_data = [];
    for (let i=0; i<learning_data.length; i++) {
        var chapter = learning_data[i];
        var temp_chapter = [chapter.chapter[0], chapter.chapter[1], []];
        for (let j=0; j<chapter.sites.length; j++) {
            var site = chapter.sites[j];
            temp_chapter[2].push([site.site[0], site.site[1]]);
        }
        site_select_data.push(temp_chapter);
    }
    console.log(site_select_data);
    return site_select_data
}

function resize_info_slides() {
    var height = $('#content').height();
    if ($(window).width() > 770) {
        var width = $('#content').width()/2 + 5;
    } else {
        var width = $('#content').width() + 25;
    }
    $('.item-info').width(width);
    $('.item-info').height(height);
}

document.addEventListener("click", function(e) {
    for (const selector in closeFunctions) {
        container = $(selector);
        if (!container.is(e.target) && container.has(e.target).length === 0) {
            if (typeof closeFunctions[selector] == 'object') {
                closeFunctions[selector].hide();
            } else {
                closeFunctions[selector]();
            }
        }
    }
}, true);

$(document).ready(function() {
    listeners();
    styles();
    site_select_data = format_site_select_data();
    site_select = new MultiLevelDropdown('module_site_select', site_select_data, 'checkbox');
    theme_select = new Dropdown('theme_select', [['option1', 1], ['option2', 2]], 'radio');
    required_for_select = new Dropdown('module_required_select', [['option1', 1], ['option2', 2]], 'checkbox');
});

$(window).resize(function() {
    resize_info_slides();
    site_select.styles();
    theme_select.styles();
    required_for_select.styles();
})

function styles() {
    resize_info_slides();
}

function listeners() {
    $('.edit-btn').on('click', show_update_info);
}