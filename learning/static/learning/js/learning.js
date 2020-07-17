class LearningTypeDropdown extends MultiLevelDropdown {
    build() {
        var elements = super.build();
        this.element.empty();
        var value = $('<h4/>')
            .text('Winter Garden Training')
            .addClass('title');
        var options = elements[3];
        options.find('input').first().prop("checked", true);
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
        this.value = [];
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
        this.element.trigger(':change');
    }

    select(site) {
        this.element.find('.site input').each(function() {
            $(this).prop("checked", false);
        });
        var site_input = $(site).find('input');
        site_input.prop("checked", true);
        this.value = [site_input.val()];
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


class LearningList extends JqueryElement {
    constructor(id) {
        super();
        this.element = $('#' + id);
        this.site_select = new MenuSiteSelect('menu');
        var type_data = this.get_type_select_data();
        this.type_select = new LearningTypeDropdown('learning_type_select', type_data, 'radio', 'Winter Garden Training');
        this.update_items();
        this.listeners();
    }

    update_items() {
        this.update_title(); // Update title with items
        resize_info_slides(); // Could change size with new title
        var site_data = null;
        var site_pk = this.site_select.value[0];
        var type = this.type_select.value[0];
        if (!(site_pk && type)) {
            return
        }
        // Get site data from learning_data
        for (let i=0; i<learning_data.length; i++) {
            var chapter = learning_data[i];
            for (let j=0; j<chapter.sites.length; j++) {
                var site = chapter.sites[j];
                if (site.site[1] == site_pk) {
                    site_data = site;
                    break
                }
            }
            if (site_data) {
                break
            }
        }
        if (!site_data) {
            return
        }
        if (type == 'Programming') {
            var items = site_data.programming
        } else {
            var items = [];
            // Filter for trainings that contain required position
            for (let i=0; i<site_data.themes.length; i++) {
                var theme = site_data.themes[i];
                var theme_data = [theme.theme[0], theme.theme[1], []];
                var contains_required_module = false;
                for (let j=0; j<theme.modules.length; j++) {
                    var module = theme.modules[j];
                    var required_for = module[2];
                    if (required_for.includes(type) || type == 'All') {
                        theme_data[2].push([module[0], module[1], 'active'])
                        contains_required_module = true;
                    } else {
                        theme_data[2].push([module[0], module[1], 'inactive'])
                    }
                }
                if (contains_required_module) {
                    items.push(theme_data);
                }
            }
        }
        this.build_items(items);
    }

    update_title() {
        var site = this.site_select.element.find(':checked').siblings('a').text();
        var type = this.type_select.value[0];
        if (type == 'All') {
            type = 'Training';
        } else if (type != 'Programming') {
            type = type + ' Training';
        }
        this.type_select.element.find('.title').text(site + ' ' + type);
    }

    get_type_select_data() {
        var training_options = [['All', 'All']].concat(role_positions);
        training_options = training_options.slice(0, -1); // Remove Other option
        var data = [['Programming', 'Programming', []], ['Training', 'Training', training_options]];
        return data
    }

    listeners() {
        this.site_select.element.on(':change', {func: this.update_items, object: this}, this.dispatch);
        this.type_select.element.on(':change', {func: this.update_items, object: this}, this.dispatch);
    }

    build_items(items) {
        this.element.empty();
        for (let i=0; i<items.length; i++) {
            var item_data = items[i];
            var item_container = $('<li/>').addClass('item');
            var item_element = $('<a/>')
                .attr('href', '#')
                .attr('value', item_data[1])
                .text(item_data[0]);
            item_container.append(item_element);
            var sub_items = item_data[2];
            sub_items = (sub_items) ? sub_items : [];
            for (let j=0; j<sub_items.length; j++) {
                var sub_data = sub_items[j];
                var sub_element = $('<a/>')
                    .addClass('sub-item')
                    .addClass(sub_data[2])
                    .attr('href', '#')
                    .attr('value', sub_data[1])
                    .text(sub_data[0]);
                item_container.append(sub_element);
            }
            this.element.append(item_container);
        }
    }
}






function show_update_info() {
    $(this).closest('item-info').find('update').show();
    $(this).hide();
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

$(document).ready(function() {
    new LearningList('items');
    listeners();
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