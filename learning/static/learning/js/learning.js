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


class FacilitatorInput extends AutocompleteInput {
    constructor(id, site_select) {
        super(id, url_learning_models);
        this.site_select = site_select;
        this.list = this.element.find('.facilitator-list');
        this.update_value();
    }

    add_facilitator_str(element, e) {
        // either clicked enter or button
        if (($(element).is('input') && e.which == 13) || $(element).is('a')) {
            if (this.input.val() == '') {
                return
            }
            this.build_item(this.input.val());
            this.update_value();
            this.input.val('');
            this.hide();
            this.scroll_list();
        }
    }

    autocomplete_select(option) {
        this.build_item({'name': $(option).text(), 'pk': $(option).attr('value')});
        this.update_value();
        this.input.val('');
        this.hide();
        this.scroll_list();
    }

    delete_facilitator(btn) {
        $(btn).closest('.profile').remove();
        this.update_value();
    }

    update_value() {
        var value = [];
        this.list.find('.profile').each(function() {
            var item = $(this).children().first();
            var name = item.text();
            var pk = item.attr("value");
            if (pk) {
                value.push({'name': name, 'pk': pk});
            } else {
                value.push(name);
            }
        });
        this.value = JSON.stringify(value);
        this.element.trigger(":change");
    }

    set_value(value) {
        this.list.empty();
        value = JSON.parse(value);
        for (let i=0; i<value.length; i++) {
            this.build_item(value[i]);
        }
        this.update_value();
    }

    scroll_list() {
        this.list.animate({ scrollTop: this.list.prop("scrollHeight")}, 1000);
    }

    get_query_data() {
        var data = {
            "site_pk": this.site_select.value[0],
            "autocomplete_facilitator_search": this.input.val(),
        };
        this.query_data = data;
    }

    listeners() {
        super.listeners();
        this.element.find('.add-facilitator-btn').click({func: this.add_facilitator_str, object: this}, this.dispatch);
        this.input.keypress({func: this.add_facilitator_str, object: this}, this.dispatch);
        this.item_listeners();
    }

    item_listeners() {
        this.element.find('.profile .fa-times').off("click");
        this.element.find('.profile .fa-times').click({func: this.delete_facilitator, object: this}, this.dispatch);
    }

    build_item(info) {
        var profile_container = $('<div/>')
            .addClass('profile');
        if (typeof(info) == 'string') {
            var profile = $('<p/>')
                .text(info);
        } else {
            var profile = $('<a/>')
                .attr("href", url_profile_detail.slice(0,-2) + info['pk'])
                .attr("value", info["pk"])
                .attr("target", '_blank')
                .text(info['name']);
        }
        var delete_btn = $('<a/>')
            .attr("href", "#")
            .addClass("fas fa-times")
            .addClass("blacklink");
        profile_container.append(profile);
        profile_container.append(delete_btn);
        this.list.append(profile_container);
        this.item_listeners();
    }

    build() {
        var temp_element = this.element;
        this.element = this.element.find('.autocomplete-input');
        super.build();
        this.element = temp_element;
        var add_btn = $("<a/>")
            .attr("href", "#")
            .addClass("fas fa-plus add-facilitator-btn blacklink");
        var match_instruction_container = $('<div/>')
            .addClass("item instruction");
        var match_instruction = $('<p/>')
            .text("Select to Link Profile");
        match_instruction_container.append(match_instruction);
        this.element.find(".no-match").before(match_instruction_container);
        this.element.find(".autocomplete-input").append(add_btn);
    }
}


class InfoSlide extends JqueryElement {
    constructor(id, type) {
        super(id)
        this.type = type;
        this.model_infos = [];
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
            this.facilitator_input = new FacilitatorInput(type + '_facilitator_input', this.site_select);
            custom_fields['facilitators'] = this.facilitator_input;
        }
        if (this.element.find('#' + type + '_link_input')) {
            this.link_input = new LinkInput(type + '_link_input');
            custom_fields['links'] = this.link_input;
        }
        this.update_form = new CustomForm(type + '_form', custom_fields, type + '_');
        this.loader_element = this.element.find('.loading');
        this.title_element = this.element.find('#' + this.type + '_title');
        this.listeners();
        this.resize();
    }

    show(pk, title, site, theme_options=null, theme=null) {
        this.base_info = {'title': title, "pk": pk};
        console.log(this.base_info)
        this.loader_element.show();
        this.site_select.set_value(site);
        if (theme) {
            this.base_info['theme'] = theme[0];
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
        console.log(data)
        $.ajax({
            url: url_learning_models,
            method: 'GET',
            data: data,
            context: this,
            success: this.model_info_success,
            complete: this.model_info_complete,
            error: this.model_info_error,
        });
    }

    model_info_success(data) {
        this.update_form.set_data(data);
        this.item_listeners(); // Item specific listeners
        this.update_model_infos();
    }

    model_info_complete(self, timeup) {
        if (timeup=='timeup') {
            self.loader_element.hide();
        } else {
            setTimeout(this.model_info_complete, 300, this, timeup='timeup');
        }
    }

    model_info_error() {
        this.hide();
        addAlertHTML("Something Went Wrong", 'danger');
    }

    hide() {
        this.erase_data();
        this.element.removeClass('show');
    }

    update_model_infos() {
        var themes = null;
        if (this.theme_select) {
            var themes = this.theme_select.value;
        }
        var title = this.title_element.val();
        var data = {
            'build_infos': true,
            'model_type': this.type,
            'base_info': JSON.stringify(this.base_info),
            'sites': JSON.stringify(this.site_select.value),
            'themes': JSON.stringify(themes),
            'title': title,
        }
        $.ajax({
            url: url_learning_models,
            method: 'GET',
            data: data,
            context: this,
            success: function(data) {
                this.model_infos = data['results'];
                this.mode = data['mode'];
                console.log(this.model_infos);
            },
        });
    }

    submit_form() {
        console.log(this.model_infos);
        var data = {
            'form': this.update_form.element.serialize(),
            'model_type': this.type,
            'fields': 'all',
            'models': JSON.stringify(this.model_infos),
        }
        var csrftoken = $('[name = "csrfmiddlewaretoken"]').val();
        $.ajax({
            url: url_learning_models,
            type: 'post',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            data: data,
            context: this,
            beforeSend: function() {
                this.loader_element.show();
            },
            success: this.submit_success,
            complete: function () {
            },
            error: function() {
            },
        });
    }

    submit_success(data) {
        this.loader_element.hide();
        // Update all model infos
        this.model_infos = data['infos'];
        // Update base info
        for (let i=0; i<data['infos'].length; i++) {
            var model_info = data['infos'][i];
            if (model_info['pk'] == this.base_info['pk']) {
                this.base_info = model_info;
            }
        }
        var title = this.base_info.title;
        if (this.base_info.hasOwnProperty('theme')) {
            title = this.base_info.theme + ' - ' + title;
        }
        this.element.find('.title-text').first().text(title);
        this.title_element
        this.element.trigger(":submit");
    }

    show_update_info() {
        $(this).closest('item-info').find('update').show();
        $(this).hide();
    }

    erase_data() {
    }

    resize() {
        var height = $('#content').height();
        if ($(window).width() > 770) {
            var width = $('#content').width()/2 + 5;
        } else {
            var width = $('#content').width() + 25;
        }
        this.element.width(width);
        this.element.height(height);
    }

    listeners() {
        this.element.find('.back').click({func: this.hide, object: this}, this.dispatch);
        this.element.find('.edit-btn').click({func: this.show_update_info, object: this}, this.dispatch);
        this.element.find('.save-btn').click({func: this.submit_form, object: this}, this.dispatch);
        $(window).resize({func: this.resize, object: this}, this.dispatch);
    }

    item_listeners() {
        if (this.theme_select) {
            this.theme_select.element.off(":change");
            this.theme_select.element.on(":change", {func: this.update_model_infos, object: this}, this.dispatch);
        }
        this.site_select.element.off(":change");
        this.site_select.element.on(":change", {func: this.update_model_infos, object: this}, this.dispatch);
        this.title_element.off("change");
        this.title_element.change({func: this.update_model_infos, object: this}, this.dispatch);
    }
}


class LearningList extends JqueryElement {
    constructor(id) {
        super(id);
        this.site_data = null;
        this.site_select = new MenuSiteSelect('menu');
        var type_data = this.get_type_select_data();
        this.type_select = new LearningTypeDropdown('learning_type_select', type_data, 'radio', 'Winter Garden Training');
        this.programming_slide = new InfoSlide('programming_info', 'programming');
        this.theme_slide = new InfoSlide('theme_info', 'theme');
        this.module_slide = new InfoSlide('module_info', 'module');
        this.slides = [this.programming_slide, this.theme_slide, this.module_slide]
        this.active_slide = null;
        this.get_items();
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
            this.active_slide = this.programming_slide;
        } else if ($(item).hasClass('sub-item')) {
            var theme_options = [];
            this.element.find('.item').each(function() {
                theme_options.push([$(this).text(), $(this).text()])
            });
            var theme = $(item).siblings('.item')
            var theme_value = [theme.text(), theme.attr("value")];
            this.module_slide.show(pk, title, this.site_select.value, theme_options, theme_value);
            this.active_slide = this.module_slide
        } else {
            this.theme_slide.show(pk, title, this.site_select.value);
            this.active_slide = this.theme_slide;
        }
    }

    get_items() {
        $.ajax({
            url: url_learning_models,
            type: 'get',
            data: {
                'get_site_models': true,
                'site': this.site_select.value[0],
            },
            context: this,
            success: function(data) {
                this.site_data = data['site_data'];
                this.update_items();
            },
        });
    }

    update_items() {
        this.update_title(); // Update title with items
        var type = this.type_select.value[0];
        if (!(this.site_data && type)) {
            return
        }
        if (type == 'Programming') {
            var items = this.site_data.programming
        } else {
            var items = [];
            // Filter for trainings that contain required position
            for (let i=0; i<this.site_data.themes.length; i++) {
                var theme = this.site_data.themes[i];
                var theme_data = [theme.theme[0], theme.theme[1], []];
                var contains_required_module = false;
                if (type == 'All') {
                    contains_required_module = true;
                }
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

    hide_resize_slides() {
        for (let i=0; i<this.slides.length; i++) {
            this.slides[i].hide();
            this.slides[i].resize();
        }
    }

    listeners() {
        this.site_select.element.on(':change', {func: this.get_items, object: this}, this.dispatch);
        this.site_select.element.on(':change', {func: this.hide_resize_slides, object: this}, this.dispatch);
        this.type_select.element.on(':change', {func: this.update_items, object: this}, this.dispatch);
        this.type_select.element.on(':change', {func: this.hide_resize_slides, object: this}, this.dispatch);
        for (let i=0; i<this.slides.length; i++) {
            this.slides[i].element.on(":submit", {func: this.get_items, object: this}, this.dispatch);
        }
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
                .addClass('item blacklink')
                .attr('href', '#')
                .attr('value', item_data[1])
                .text(item_data[0]);
            item_container.append(item_element);
            var sub_items = item_data[2];
            sub_items = (sub_items) ? sub_items : [];
            for (let j=0; j<sub_items.length; j++) {
                var sub_data = sub_items[j];
                var sub_element = $('<a/>')
                    .addClass('sub-item blacklink')
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

//function resize_info_slides() {
//    var height = $('#content').height();
//    if ($(window).width() > 770) {
//        var width = $('#content').width()/2 + 5;
//    } else {
//        var width = $('#content').width() + 25;
//    }
//    $('.item-info').width(width);
//    $('.item-info').height(height);
//}

$(document).ready(function() {
    new LearningList('items');
//    listeners();
//    resize_info_slides();
});


function listeners() {
    $(window).resize(resize_info_slides);
}