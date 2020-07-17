class LearningTypeDropdown extends MultiLevelDropdown {
    build() {
        var elements = super.build();
        this.element.empty();
        var value = $('<h4/>')
            .text('Winter Garden Training')
            .addClass('title')
            .addClass('value');
        this.element.append(value);
        this.element.append(elements[1]);
        this.element.append(elements[2]);
        this.element.append(elements[3]);
    }
}


class MenuSiteSelect extends JqueryElement {
    constructor(id) {
        super()
        this.id = id;
        this.element = $('#' + id);
        this.listeners();
        this.show_sites(this.element.find('.chapter')[0]);
        this.select(this.element.find('.site')[0]);
    }

    listeners() {
        $('#menu_btn').click({func: this.show, object: this}, this.dispatch);
        this.element.find('.back').click({func: this.hide, object: this}, this.dispatch);
        this.element.find('.chapter').click({func: this.show_sites, object: this}, this.dispatch);
        this.element.find('.site').click({func: this.change, object: this}, this.dispatch);
    }

    show_sites(chapter) {
        this.element.find('.site-select').children().each(function() {
            $(this).find('.sites').hide();
            $(this).removeClass('shadow')
        })
        $(chapter).addClass('shadow');
        $(chapter).find('.sites').show();
    }

    change(site) {
        this.select(site);
        this.element.trigger(':changed');
    }

    select(site) {
        this.element.find('.site input').each(function() {
            $(this).prop("checked", false);
        });
        $(site).find('input').prop("checked", true);
    }

    show() {
        this.element.addClass('show');
        closeFunctions['#' + this.id] = this;
    }

    hide() {
        this.element.removeClass('show');
        delete closeFunctions['#' + this.id];
    }
}

function show_update_info() {
    $(this).closest('item-info').find('update').show();
    $(this).hide();
}

function get_type_select_data() {
    var training_options = [['All', 'All']].concat(role_positions);
    training_options = training_options.slice(0, -1); // Remove Other option
    var data = [['Training', 'Training', training_options], ['Programming', 'Programming', []]];
    return data
}

function get_site_select_data() {
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
    new MenuSiteSelect('menu');
    type_select_data = get_type_select_data();
    new LearningTypeDropdown('learning_type_select', type_select_data, 'radio', 'Winter Garden Training');
    site_select_data = get_site_select_data();
    new MultiLevelDropdown('programming_site_select', site_select_data, 'checkbox', 'Site');
    new MultiLevelDropdown('theme_site_select', site_select_data, 'checkbox', 'Site');
    new MultiLevelDropdown('module_site_select', site_select_data, 'checkbox', 'Site');
    new Dropdown('theme_select', [['option1', 1], ['option2', 2]], 'checkbox', 'Theme');
    new Dropdown('module_required_select', [['option1', 1], ['option2', 2]], 'checkbox', 'Required For');
//    new Modal('modal', 'Are You Sure?', ['Delete Programming?'], function() {console.log('action');});
    resize_info_slides();
});


function listeners() {
    $('.edit-btn').on('click', show_update_info);
    $(window).resize(resize_info_slides);
}