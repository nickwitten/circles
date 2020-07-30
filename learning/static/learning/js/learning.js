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
        this.value = "[]";
        this.default_value = "[]";
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
            var pk = parseInt(item.attr("value"));
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




class ModelTitleAutocomplete extends AutocompleteInput {
    constructor(id, type) {
        super(id, url_learning_models);
        this.type = type
        this.default_value = '';
    }

    get_query_data() {
        this.query_data = {
            'model_type': this.type,
            'autocomplete_search': this.input.val(),
        }
    }
}




class UpdateForm extends CustomForm {
    constructor(id, custom_fields, form_fields, field_prefix) {
        super(id, custom_fields, form_fields, field_prefix);
        this.edit_fields = 'all';
        this.hidden_fields = [];
    }

    hide_all_fields(visible) {
        this.hidden_fields = [];
        this.edit_fields = visible;
        for (const field in this.form_fields) {
            if (!visible.includes(field)) {
                this.hidden_fields.push(field);
                if (this.custom_fields[field]) {
                    this.custom_fields[field].element.closest('.field-row').hide();
                } else {
                    this.element.find('#' + this.field_prefix + field).closest('.field-row').hide();
                }
            }
        }
        this.element.find('.edit-more-btn').show();
    }

    show_fields(visible) {
        if (visible == 'all') {
            visible = Object.keys(this.form_fields);
        }
        for (let i=0; i<visible.length; i++) {
            var field = visible[i];
            // Add to edit fields
            if (typeof(this.edit_fields) == 'object' && !this.edit_fields.includes(field)) {
                this.edit_fields.push(field);
            }
            // Remove from hidden fields
            var hidden_index = this.hidden_fields.indexOf(field)
            if (hidden_index != 1) {
                this.hidden_fields.splice(hidden_index, 1);
            }
            // Show element
            if (this.custom_fields[field]) {
                this.custom_fields[field].element.closest('.field-row').show();
            } else {
                this.element.find('#' + this.field_prefix + field).closest('.field-row').show();
            }
        }
        // Check if all are added
        if (Object.keys(this.form_fields).length == this.edit_fields.length) {
            this.element.find('.edit-more-btn').hide();
            this.edit_fields = 'all';
        }
    }

    get_fields_modal() {
        var visible = []
        this.modal.element.find('input').each(function() {
            if ($(this).prop('checked') && $(this).val() != 'all') {
                visible.push($(this).val());
            }
        });
        this.show_fields(visible);
    }

    show_fields_modal() {
        var hidden_fields = this.hidden_fields;
        hidden_fields = ['all'].concat(hidden_fields);
        var build_modal = function() {
            this.element.find('.header-text').text('Edit Fields');
            this.element.find('.action.btn').attr('class', 'btn action');
            this.element.find('.action.btn').addClass('btn action btn-primary');
            this.element.find('.content-container').empty();
            for (let i=0; i<hidden_fields.length; i++) {
                var option_container = $('<div/>')
                    .addClass('option-container');
                var option_input = $('<input/>')
                    .attr('type', 'checkbox')
                    .val(hidden_fields[i]);
                var text = hidden_fields[i].split("_").join(" ");
                var option_text = $('<p/>')
                    .text(text[0].toUpperCase() + text.slice(1));
                var click_wrapper = $('<a/>')
                    .attr("href", "#")
                    .addClass("click-wrapper");
                option_container.append(option_input);
                option_container.append(option_text);
                option_container.append(click_wrapper);
                this.element.find('.content-container').append(option_container);
            }
            this.element.find('.option-container').click(function() {
                var input = $(this).find('input');
                input.prop("checked", !input.prop("checked"));
                // check all if all input picked
                if (input.val() == 'all') {
                    $(this).closest('.content-container').find('input').each(function() {
                        $(this).prop("checked", input.prop('checked'));
                    });
                }
            });
        }
        this.modal = new Modal('modal', {
            'action_func': this.dispatch,
            'action_data': {object: this, func: this.get_fields_modal},
            'build_func': build_modal,
        });
    }

    listeners() {
        super.listeners();
        this.element.find('.edit-more-btn').click({func: this.show_fields_modal, object: this}, this.dispatch)

    }
}




class InfoSlide extends JqueryElement {
    constructor(id, type) {
        super(id)
        this.type = type;
        this.model_infos = [];
        this.site_select = new MultiLevelDropdown(type + '_site_select', this.get_site_select_data());
        this.title_input = new ModelTitleAutocomplete(type + '_title_input', type);
        this.theme_select = null; // Will be created on module show
        this.required_select = null;
        var custom_fields = {'title': this.title_input};
        if (this.element.find('#' + type + '_required_select').length) {
            this.required_select = new JsonDropdown(type + '_required_select', role_positions.slice(0,-1));
            custom_fields['required_for'] = this.required_select;
        }
        if (this.element.find('#' + type + '_facilitator_input').length) {
            this.facilitator_input = new FacilitatorInput(type + '_facilitator_input', this.site_select);
            custom_fields['facilitators'] = this.facilitator_input;
        }
        if (this.element.find('#' + type + '_link_input').length) {
            this.link_input = new LinkInput(type + '_link_input');
            custom_fields['links'] = this.link_input;
        }
        if (this.element.find('#' + type + '_file_input').length) {
            this.file_input = new FileInput(type + '_file_input');
            custom_fields['files'] = this.file_input;
        }
        this.update_form = new UpdateForm(type + '_form', custom_fields, form_fields[type], type + '_');
        this.loader_element = this.element.find('.loading');
        this.listeners();
        this.resize();
    }

    show_create(site, {theme_options=null, required_for=null} = {}) {
        this.info_update_listeners_off();
        this.mode = 'create';
        this.base_info = {'site': parseInt(site[0]), 'title': ''}
        this.update_form.show_fields('all');
        this.site_select.set_value(site);
        if (theme_options) {
            delete this.theme_select;
            this.theme_select = new Dropdown(this.type + '_theme_select', theme_options);
            this.theme_select.set_value(this.theme_select.default_value);
            this.base_info['theme'] = '';
        }
        if (required_for) {
            this.required_select.set_value(JSON.stringify(required_for));
        }
        this.element.find('.title-text').first().text('Create New ' + this.type[0].toUpperCase() + this.type.slice(1));
        this.element.addClass('show');
        this.item_listeners();
    }

    show_model(pk, title, site, theme_options=null, theme=null) {
        this.info_update_listeners_off();
        this.base_info = {'site': parseInt(site[1]), 'site_str': site[0], 'title': title, "pk": pk};
        this.model_infos = [this.base_info];
        this.mode = 'update';
        this.update_form.show_fields('all');
        this.loader_element.show();
        this.site_select.set_value([site[1]]);
        if (theme) {
            this.base_info['theme'] = theme[0];
            title = theme[0] + ' - ' + title;
            if (this.theme_select) {
                this.theme_select.element.empty(); // delete previous
            }
            this.theme_select = new Dropdown(this.type + '_theme_select', theme_options);
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
            context: this,
            success: this.model_info_success,
            error: this.model_info_error,
        });
    }

    model_info_success(data) {
        this.loader_element.hide();
        this.update_form.set_data(data);
        this.item_listeners(); // Item specific listeners
    }

    delayed_loader_hide(self, timeup) {
        if (timeup=='timeup') {
            self.loader_element.hide();
        } else {
            setTimeout(this.delayed_loader_hide, 300, this, timeup='timeup');
        }
    }

    model_info_error() {
        this.hide();
        addAlertHTML("Something Went Wrong", 'danger');
        this.delayed_loader_hide();
    }

    hide() {
        this.info_update_listeners_off();
        this.element.removeClass('show');
        this.delayed_erase_data(this, "timeup");
    }

    delayed_erase_data(self, timeup) {
        if (timeup=='timeup') {
            self.update_form.erase_data();
        } else {
            setTimeout(this.delayed_erase_data, 300, this, 'timeup');
        }
    }

    update_required_for({required_for=null} = {}) {
        if (required_for) {
            // Set module requirements to theme requirements
            if (required_for.length) {
                this.required_select.set_value(JSON.stringify(required_for));
                this.required_select.show();
            }
            this.theme_select.hide();
        } else if (this.mode == 'create') {
            this.element.trigger(':required_for');
        }
    }

    update_model_infos() {
        this.info_update_listeners_off();
        if ((this.mode == 'move' || this.mode == 'create') && this.theme_select) {
            if (this.theme_select.value.length > 1) {
                this.theme_select.set_value([this.base_info['theme']]);
                addAlertHTML('Please Save Before Copying to Other Themes', 'secondary');
                this.item_listeners();
                return
            }
        } else if (this.mode == 'copy' && (this.title_input.value != this.base_info['title'])) {
            this.title_input.set_value(this.base_info['title']);
            addAlertHTML('Please Save Before Copying to Other Themes', 'secondary');
            this.item_listeners();
            return
        }
        this.item_listeners();
        var themes = null;
        if (this.theme_select) {
            var themes = this.theme_select.value;
            if (!themes.length) {
                return
            }
        }
        var title = this.title_input.value;
        if (!title) {
            return
        }
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
            beforeSend: function() {
                this.loader_element.show();
            },
            success: this.build_model_infos_success,
            error: this.build_model_infos_error,
            complete: function() {
                this.loader_element.hide();
            },
        });
    }

    build_model_infos_success(data) {
        this.model_infos = data['results'];
        // Update mode
        if (this.mode == 'create' && data['mode'] == 'move') {
            // Keep in create mode
            this.mode = 'create';
        } else {
            this.mode = data['mode'];
        }
        var warning_infos = []
        for (let i=0; i<this.model_infos.length; i++) {
            var info = this.model_infos[i];
            // If moving notify about base and replace
            if (this.mode == 'move' && info.hasOwnProperty('pk')) {
                // Do something
            }
            // Pass notifying about base model and created models
            if (!((info.pk == parseInt(this.base_info.pk) && !info.hasOwnProperty('replace_pk'))
                || (!info.hasOwnProperty('pk')))) {
                warning_infos.push(info);
            }
        }
        this.alert_overwrite('update', warning_infos);
        if (this.model_infos.length > 1) {
            // collapse form and only edit title
            this.update_form.hide_all_fields(['title']);
        }
    }

    alert_overwrite(action, model_infos) {
        var overwrite_warnings = [];
        for (let i=0; i<model_infos.length; i++) {
            var info = model_infos[i];
            var title = info['title'];
            var site = info['site_str'];
            if (info.hasOwnProperty('theme')) {
                title = info['theme'] + ' - ' + title;
            } else if (action == 'delete' && this.type == 'theme') {
                title = title + ' - and containing modules';
            }
            var added = false;
            for (let j=0; j<overwrite_warnings.length; j++) {
                if (site == overwrite_warnings[j]['site']) {
                    overwrite_warnings[j]['items'].push(title);
                    added = true;
                }
            }
            if (!added) {
                overwrite_warnings.push({'site': site, 'items': [title]});
            }
        }
        var modal_build_func = function() {
            var header = (action == 'delete') ? 'Would You Like to Delete the Following' :
            'Would You Like to Overwrite the Following?';
            this.element.find('.action.btn').attr('class', 'btn action');
            this.element.find('.action.btn').addClass('btn action btn-danger');
            this.element.find('.header-text').text(header);
            this.modal_element.find('.content-container').empty();
            for (let i=0; i<overwrite_warnings.length; i++) {
                var container = $('<div/>').addClass('m-2');
                container.append(
                    $('<h6/>').text(overwrite_warnings[i]['site']).addClass('mb-2 mt-2')
                );
                for (let j=0; j<overwrite_warnings[i]['items'].length; j++) {
                    container.append(
                        $('<p/>').text(overwrite_warnings[i]['items'][j]).addClass('m-1')
                    );
                }
                this.modal_element.find('.content-container').append(container);
            }
        }
        if (overwrite_warnings.length) {
            if (action == 'update') {
                new Modal('modal', {
                    build_func: modal_build_func,
                    cancel_func:this.dispatch,
                    cancel_data:{object: this, func: this.reset_model_info},
                    escapable:false
                });
            } else if (action == 'delete') {
                new Modal('modal', {
                    build_func: modal_build_func,
                    action_func:this.dispatch,
                    action_data:{object: this, func: this.delete_submit, extra_data: model_infos},
                });
            }
        }
    }

    build_model_infos_error() {
        addAlertHTML("Something Went Wrong", 'danger');
        this.reset_model_info();
    }

    reset_model_info() {
        this.info_update_listeners_off();
        this.site_select.set_value([this.base_info["site"]]);
        if (this.theme_select) {
            this.theme_select.set_value([this.base_info["theme"]]);
        }
        this.title_input.set_value(this.base_info["title"]);
        this.item_listeners();
    }

    submit_form() {
        if (!(this.title_input.value)) {
            addAlertHTML('Title Required', 'danger');
            return
        }
        if (this.type=='module' && !this.theme_select.value.length) {
            addAlertHTML('Theme Required', 'danger');
            return
        }
        var fields = this.update_form.edit_fields;
        if (typeof(fields) != 'string') {
            fields = JSON.stringify(fields);
        }
        var set_files = (this.base_info.hasOwnProperty("pk")) ? this.base_info["pk"] : null;
        if (this.file_input) {
            var data = this.file_input.form_data;
            var delete_files = JSON.stringify(this.file_input.delete_files);
            var set_files = (this.base_info.hasOwnProperty("pk")) ? this.base_info["pk"] : null;
            data.append('delete_files', delete_files);
            data.append('set_files', set_files)
        } else {
            var data = new FormData()
        }
        data.append('form', this.update_form.element.serialize());
        data.append('model_type', this.type);
        data.append('fields', fields);
        data.append('models', JSON.stringify(this.model_infos));
        console.log(data);
        var csrftoken = $('[name = "csrfmiddlewaretoken"]').val();
        $.ajax({
            url: url_learning_models,
            type: 'post',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            data: data,
            processData: false,
            contentType: false,
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
            var match = false;
            if (!this.base_info['pk']) {
                // Model was just created
                if (this.base_info['site'] == model_info['site']) {
                    match = true;
                }
            } else if (model_info['pk'] == this.base_info['pk']) {
                match = true;
            }
            if (match) {
                this.base_info = model_info;
                console.log(model_info);
                if (this.hasOwnProperty('file_input')) {
                    this.file_input.set_value(JSON.parse(model_info['files']));
                }
            }
        }
        var title = this.base_info.title;
        if (this.base_info.hasOwnProperty('theme')) {
            title = this.base_info.theme + ' - ' + title;
        }
        this.mode = 'update';
        this.element.find('.title-text').first().text(title);
        this.element.trigger(":submit");
        console.log(this.model_infos)
    }

    delete_models() {
        if (this.mode == 'move' || this.mode == 'create') {
            addAlertHTML('Please Save Before Deleting', 'secondary');
            return
        }
        var delete_infos = []
        for (let i=0; i<this.model_infos.length; i++) {
            if (this.model_infos[i].hasOwnProperty('pk')) {
                delete_infos.push(this.model_infos[i]);
            }
        }
        this.alert_overwrite('delete', delete_infos);
    }

    delete_submit(button, e, model_infos) {
        var csrftoken = $('[name = "csrfmiddlewaretoken"]').val();
        $.ajax({
            url: url_learning_models,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            data: {
                'delete': true,
                'model_type': this.type,
                'models': JSON.stringify(model_infos),
            },
            context: this,
            beforeSend: function() {
                this.loader_element.show();
            },
            success: this.delete_success,
            error: this.delete_error,
            complete: function() {
                this.loader_element.hide();
            },
        });
    }

    delete_success() {
        this.hide();
        this.element.trigger(':submit');
    }

    delete_error() {
        addAlertHTML('Something Went Wrong', 'danger');
    }

    show_update_info() {
        $(this).closest('item-info').find('update').show();
        $(this).hide();
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

    get_site_select_data() {
        var site_select_data = [];
        for (let i=0; i<user_sites.length; i++) {
            var chapter = user_sites[i];
            var temp_chapter = [chapter.chapter[0], chapter.chapter[1], []];
            for (let j=0; j<chapter.sites.length; j++) {
                var site = chapter.sites[j];
                temp_chapter[2].push([site[0], site[1]]);
            }
            site_select_data.push(temp_chapter);
        }
        return site_select_data
    }

    info_update_listeners_off() {
        if (this.theme_select) {
            this.theme_select.element.off(":change.update");
        }
        this.site_select.element.off(":change.update");
        this.title_input.element.off(":change.update");
    }

    listeners() {
        this.element.find('.back').click({func: this.hide, object: this}, this.dispatch);
        this.element.find('.edit-btn').click({func: this.show_update_info, object: this}, this.dispatch);
        this.element.find('.delete-btn').click({func: this.delete_models, object: this}, this.dispatch);
        this.element.find('.save-btn').click({func: this.submit_form, object: this}, this.dispatch);
        $(window).resize({func: this.resize, object: this}, this.dispatch);
    }

    item_listeners() {
        this.info_update_listeners_off(); // reset
        if (this.theme_select) {
            this.theme_select.element.on(":change.update", {func: this.update_model_infos, object: this}, this.dispatch);
            this.theme_select.element.off(":change.required");
            this.theme_select.element.on(":change.required", {func: this.update_required_for, object: this}, this.dispatch);
        }
        this.site_select.element.on(":change.update", {func: this.update_model_infos, object: this}, this.dispatch);
        this.title_input.element.on(":change.update", {func: this.update_model_infos, object: this}, this.dispatch);
    }
}




class LearningList extends JqueryElement {
    constructor(id) {
        super(id);
        this.site_data = null;
        this.site_select = new MenuSiteSelect('menu');
        var type_data = this.get_type_select_data();
        this.type_select = new LearningTypeDropdown('learning_type_select', type_data, {type: 'radio'});
        this.programming_slide = new InfoSlide('programming_info', 'programming');
        this.theme_slide = new InfoSlide('theme_info', 'theme');
        this.module_slide = new InfoSlide('module_info', 'module');
        this.slides = [this.programming_slide, this.theme_slide, this.module_slide]
        this.active_slide = null;
        this.create_programming = $('#create_programming');
        this.create_theme = $('#create_theme');
        this.create_module = $('#create_module');
        this.loader_element = this.element.siblings('.loading');
        this.get_items();
        this.listeners();
    }

    show_item_info(item) {
        var type = this.type_select.value[0];
        var title = $(item).text();
        var pk = $(item).attr('value');
        var site_val = this.site_select.value;
        var site = null
        this.site_select.element.find('input').each(function () {
            if ($(this).val() == site_val[0]) {
                site = [$(this).siblings('.site-name').text(), $(this).val()]
            }
        });
        this.programming_slide.hide();
        this.theme_slide.hide();
        this.module_slide.hide();
        if (type == 'Programming') {
            this.programming_slide.show_model(pk, title, site);
            this.active_slide = this.programming_slide;
        } else if ($(item).hasClass('sub-item')) {
            var theme_options = this.get_theme_select_data();
            var theme = $(item).siblings('.item')
            var theme_value = [theme.text(), theme.attr("value")];
            this.module_slide.show_model(pk, title, site, theme_options, theme_value);
            this.active_slide = this.module_slide
        } else {
            this.theme_slide.show_model(pk, title, site);
            this.active_slide = this.theme_slide;
        }
    }

    create_model(button) {
        var site = this.site_select.value
        if (button.id == 'create_programming') {
            this.programming_slide.show_create(site);
        } else if (button.id == 'create_theme') {
            this.theme_slide.show_create(site, {required_for: this.type_select.value});
        } else if (button.id == 'create_module') {
            this.module_slide.show_create(site, {theme_options: this.get_theme_select_data()});
        }
    }

    update_required_for() {
    // If user is creating module, call with required_for data from chosen theme
        if (this.module_slide.mode == 'create') {
            var theme = [];
            if (this.module_slide.theme_select) {
                theme = this.module_slide.theme_select.value
            }
            var theme = (theme.length) ? theme[0] : null;
            for (let i=0; i<this.site_data.themes.length; i++) {
                var theme_info = this.site_data.themes[i].theme;
                if (theme_info[0] == theme) {
                    this.module_slide.update_required_for({required_for: theme_info[2]});
                    return
                }
            }
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
            beforeSend: function() {
                this.loader_element.show();
            },
            success: function(data) {
                this.site_data = data['site_data'];
                this.update_items();
            },
            error: function() {
                addAlertHTML("Something Went Wrong", 'danger');
            },
            complete: function() {
                this.loader_element.hide();
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
            this.create_programming.show();
            this.create_theme.hide();
            this.create_module.hide();
        } else {
            this.create_programming.hide();
            this.create_theme.show();
            this.create_module.show();
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
                if (contains_required_module || theme.theme[2].includes(type)) {
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

    get_theme_select_data() {
        var theme_options = [];
        this.element.find('.item').each(function() {
            theme_options.push([$(this).text(), $(this).text()])
        });
        return theme_options;
    }

    hide_resize_slides() {
        this.site_select.hide();
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
        this.module_slide.element.on(":required_for", {func: this.update_required_for, object: this}, this.dispatch);
        this.create_programming.click({func: this.create_model, object: this}, this.dispatch);
        this.create_theme.click({func: this.create_model, object: this}, this.dispatch);
        this.create_module.click({func: this.create_model, object: this}, this.dispatch);
    }

    item_listeners() {
        this.element.find('a').off("click");
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




$(document).ready(function() {
    new LearningList('items');
});