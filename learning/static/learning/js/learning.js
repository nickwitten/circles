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
        super(id);
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


class FacilitatorInput extends JqueryElement {
    constructor(id, info_slide) {
        super(id);
        this.value = [];
        this.xhr = null;
        this.input = this.element.find('input');
        this.listeners();
    }

    set_value() {

    }

    add_facilitator_str(element, e) {
        // either clicked enter or button
        if (($(element).is('input') && e.which == 13) || $(element).is('a')) {
            if (this.input.val() == '') {
                return
            }
            this.build_item(this.input.val());
            this.input.val('');
            this.hide();
        }
    }

    add_facilitator_profile(option) {
        console.log(option);
        this.build_item([$(option).text(), $(option).attr('value')]);
        this.input.val('');
        this.hide();
    }

    autocomplete_send(input, e, site_select) {
        this.show();
        if (this.xhr) {
            this.xhr.abort();
        }
        var q = $(input).val();
        if (!q.length) {
            return this.hide();
        }
        var data = {
            'autocomplete_facilitator_search': q,
            'site_pk': site_select.value[0],
        }
        this.xhr = $.ajax({
            url: url_learning_models,
            method: 'GET',
            data: data,
            context: this,
            success: this.autocomplete_receive
        });
    }

    show() {
        this.element.find('.autocomplete').addClass('visible');
        this.element.find('.matches-wrapper').addClass('show');
        closeFunctions['.facilitators'] = this;
    }

    hide() {
        this.element.find('.matches-wrapper').removeClass('show');
        this.element.find('.autocomplete').removeClass('visible');
        delete closeFunctions['.facilitators']
    }

    autocomplete_receive(data) {
        this.xhr = null;
        console.log(data);
        this.build_matches(data['results']);
    }

    listeners() {
        this.element.find('.add-facilitator-btn').click({func: this.add_facilitator_str, object: this}, this.dispatch);
        this.input.keypress({func: this.add_facilitator_str, object: this}, this.dispatch);
        this.item_listeners();
    }

    item_listeners() {
        this.element.find('.autocomplete a').click({func: this.add_facilitator_profile, object: this}, this.dispatch);
        console.log('listeners');
        this.element.find('.profile fa-times').click({func: this.delete_facilitator, object: this}, this.dispatch);
    }

    build_matches(data) {
        this.element.find('.matches').empty();
        for (let i=0; i<data.length; i++) {
            var match_container = $('<div/>')
                .addClass("match")
                .addClass("item");
            var match = $("<a/>")
                .text(data[i][0])
                .attr("value", data[i][1])
                .addClass("blacklink")
                .attr("href", "#");
            match_container.append(match);
            this.element.find('.matches').append(match_container);
        }
        if (!data.length) {
            this.element.find('.no-match').show();
        } else {
            this.element.find('.no-match').hide();
        }
        this.item_listeners();
    }

    build_item(info) {
        var profile_container = $('<div/>')
            .addClass('profile');
        if (Array.isArray(info)) {
            var profile = $('<a/>')
                .attr("href", url_profile_detail.slice(0,-1) + toString(info[1]))
                .attr("target", '_blank')
                .text(info[0]);
        } else {
            var profile = $('<p/>')
                .text(info);
        }
        var delete_btn = $('<a/>')
            .attr("href", "#")
            .addClass("fas fa-times")
            .addClass("blacklink");
        profile_container.append(profile);
        profile_container.append(delete_btn);
        this.element.find('.facilitator-list').append(profile_container);
    }
}


class InfoSlide extends JqueryElement {
    constructor(id, type) {
        super(id)
        this.type = type;
        var site_select_data = get_site_select_data();
        this.site_select = new MultiLevelDropdown(type + '_site_select', site_select_data, 'checkbox', '');
        this.theme_select = null; // Will be created on module show
        this.required_select = null;
        var custom_fields = {};
        if (this.element.find('#' + type + '_required_select')) {
            this.required_select = new JsonDropdown(type + '_required_select', role_positions.slice(0,-1), 'checkbox', '');
            custom_fields['required_for'] = this.required_select;
        }
        if (this.element.find('#' + type + '_facilitator_input')) {
            this.facilitator_input = new FacilitatorInput(type + '_facilitator_input');
//            custom_fields['facilitators'] = this.facilitator_input;
        }
        this.update_form = new CustomForm(type + '_form', custom_fields, type + '_');
        this.listeners();
    }

    show(pk, title, site, theme_options=null, theme=null) {
        this.site_select.set_value(site);
        if (theme) {
            title = theme[0] + ' - ' + title;
            if (this.theme_select) {
                this.theme_select.element.empty(); // delete previous
            }
            this.theme_select = new Dropdown(this.type + '_theme_select', theme_options, 'checkbox', '');
            this.theme_select.set_value(theme);
        }
        this.element.find('.title-text').first().text(title);
        this.element.addClass('show');
        var data = {
            'pk': pk,
            'model_type': this.type,
        }
        $.ajax({
            url: url_learning_models,
            method: 'GET',
            data: data,
            context: this.update_form,
            success: this.update_form.set_data,
        });
    }

    hide() {
        this.erase_data();
        this.element.removeClass('show');
    }

    erase_data() {
    }

    listeners() {
        this.element.find('.back').click({func: this.hide, object: this}, this.dispatch);
        this.facilitator_input.element.find('input').on("input", {
            object: this.facilitator_input,
            func: this.facilitator_input.autocomplete_send,
            extra_data: this.site_select,
        }, this.dispatch);
    }
}


class LearningList extends JqueryElement {
    constructor(id) {
        super(id);
        this.site_select = new MenuSiteSelect('menu');
        var type_data = this.get_type_select_data();
        this.type_select = new LearningTypeDropdown('learning_type_select', type_data, 'radio', 'Winter Garden Training');
        this.programming_slide = new InfoSlide('programming_info', 'programming');
        this.theme_slide = new InfoSlide('theme_info', 'theme');
        this.module_slide = new InfoSlide('module_info', 'module');
        this.update_items();
        this.listeners();
    }

    show_item_info(item) {
        var type = this.type_select.value[0];
        var title = $(item).text();
        var pk = $(item).attr('value');
        this.programming_slide.hide();
        this.theme_slide.hide();
        this.module_slide.hide();
        if (type == 'Programming') {
            this.programming_slide.show(pk, title, this.site_select.value);
        } else if ($(item).hasClass('sub-item')) {
            var theme_options = [];
            this.element.find('.item').each(function() {
                theme_options.push([$(this).text(), $(this).attr("value")])
            });
            var theme = $(item).siblings('.item')
            var theme_value = [theme.text(), theme.attr("value")];
            this.module_slide.show(pk, title, this.site_select.value, theme_options, theme_value);
        } else {
            this.theme_slide.show(pk, title, this.site_select.value);
        }
    }

    update_items() {
        this.update_title(); // Update title with items
        resize_info_slides(); // Could change size with new title
        this.programming_slide.hide(); // Hide all slides
        this.theme_slide.hide();
        this.module_slide.hide();
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
        this.item_listeners();
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

    item_listeners() {
        this.element.find('a').click({func: this.show_item_info, object: this}, this.dispatch);
    }

    build_items(items) {
        this.element.empty();
        for (let i=0; i<items.length; i++) {
            var item_data = items[i];
            var item_container = $('<li/>').addClass('item-container');
            var item_element = $('<a/>')
                .addClass('item')
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
    new Dropdown('theme_select', [['option1', 1], ['option2', 2]], 'checkbox', 'Theme');
//    new Modal('modal', 'Are You Sure?', ['Delete Programming?'], function() {console.log('action');});
    resize_info_slides();
});


function listeners() {
    $('.edit-btn').on('click', show_update_info);
    $(window).resize(resize_info_slides);
}