var closeFunctions = {
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


function addAlertHTML(message, type) {
    $('.alert').remove();
    alert = $('<div/>')
        .addClass('alert alert-' + type)
        .text(message);
    close_btn = $('<a/>')
        .attr('href','#')
        .addClass('close fas fa-times')
        .attr('data-dismiss', 'alert')
        .attr('aria-label','close');
    alert.append(close_btn);
    $('.alert-container').append(alert);
}


class JqueryElement {
    constructor(id) {
        this.id = id
        this.element = $('#' + id);
    }

    dispatch(event) {
        var event_this = this;
        var extra_data = null;
        if (event.data.hasOwnProperty('extra_data')) {
            extra_data = event.data.extra_data;
        }
        event.data.func.call(event.data.object, event_this, event, extra_data);
    }
}

class Dropdown extends JqueryElement {
    constructor(id, data, {type='checkbox', placeholder='', default_value=[]} = {}) {
        super(id);
        this.data = data;
        this.type = type;
        this.placeholder = placeholder;
        this.default_value = default_value;
        this.value = default_value;
        this.text = '';
        this.build();
        this.styles();
        this.update_value();
        this.listeners();
    }

    listeners() {
        var dropdown = this;
        this.element.find('.show-wrapper').click({func: this.show, object: this}, this.dispatch);
        this.element.find('.option').click({func: this.select, object: this}, this.dispatch);
        $(window).resize({func: this.styles, object: this}, this.dispatch);
    }

    show() {
        var dropdown = this.element;
        dropdown.find('.options').addClass('visible');
        dropdown.find('.pointer').addClass('rotate');
        var options_wrapper = dropdown.find('.options-wrapper');
        options_wrapper.addClass('show');
        options_wrapper.css('top', '0');
        dropdown.find('.show-wrapper').hide();
        // Start checking for clicks outside
        closeFunctions['#' + this.id + ' .option'] = this;
    }

    hide() {
        var dropdown = this.element;
        dropdown.find('.options').removeClass('visible');
        dropdown.find('.pointer').removeClass('rotate');
        var options_wrapper = dropdown.find('.options-wrapper');
        options_wrapper.removeClass('show');
        options_wrapper.css('top', '-' + options_wrapper.css('height'));
        dropdown.find('.show-wrapper').show();
        // Stop checking for clicks outside
        delete closeFunctions['#' + this.id + ' .option'];
    }

    set_value(values) {
        // Uncheck all
        this.element.find('input').prop("checked", false);
        this.element.find('.value').first().text(this.placeholder);
        // Check if matches a value
        for (let i=0; i<values.length; i++) {
            var value = values[i];
            var dropdown = this;
            this.element.find('input').each(function() {
                if (value.length == 2) {
                    var match = (value[0] == $(this).siblings('p').text() && value[1] == $(this).val());
                } else {
                    var match = ($(this).val() == value);
                }
                if (match) {
                    $(this).prop("checked", true);
                }
            });
        }
        // Update this.value and displayed value
        this.update_value();
    }

    select(option, e) {
        if (this.type == 'radio') {
            this.element.find('input').prop("checked", false);
            $(option).find('input').prop("checked", true);
        } else if (this.type == 'checkbox') {
            // Check if it's already been changed
            if (e.target.type != 'checkbox') {
                var input = $(option).find('input');
                input.prop("checked", !input.prop("checked"));
            }
        }
        this.update_value();
    }

    update_value() {
        var dropdown = this;
        var value_element = this.element.find('.value').first();
        this.value = [];
        this.element.find('input').each(function() {
            if ($(this).is(':checked')) {
                dropdown.text = $(this).siblings('p').text();
                dropdown.value.push($(this).val());
            }
        });
        if (this.value.length > 1) {
            this.text = 'Multiple';
        } else if (this.value.length < 1) {
            this.text = this.placeholder;
        }
        value_element.text(this.text);
        this.element.trigger(":change");
    }

    styles() {
        var dropdown = this.element;
        var options_wrapper = dropdown.find('.options-wrapper');
        options_wrapper.css('top', '-' + options_wrapper.css('height'));
        var options = dropdown.find('.options');
        options.css('height', 'fit-content');
        options.height(options.height() + 10);
        this.hide();
    }

    build() {
        var value = $('<p/>')
            .addClass('value')
        var pointer = $('<i/>')
            .addClass('pointer fas fa-caret-left');
        var show_wrapper = $('<a/>')
            .addClass('show-wrapper')
            .attr('href', "#");
        var options = $('<div/>')
            .addClass('options');
        var options_wrapper = $('<div/>')
            .addClass('options-wrapper');
        for (let i=0; i<this.data.length; i++) {
            var option_data = this.data[i];
            var option = $('<div/>')
                .addClass('option');
            var input = $('<input/>')
                .attr('type', this.type)
                .attr('value', option_data[1])
                .prop('readonly', true);
            var option_text = $('<p/>')
                .text(option_data[0]);
            option.append(input);
            option.append(option_text);
            options_wrapper.append(option)
        }
        options.append(options_wrapper);
        this.element.empty();
        this.element.append(value);
        this.element.append(pointer);
        this.element.append(show_wrapper);
        this.element.append(options);
        return [value, pointer, show_wrapper, options]
    }
}


class JsonDropdown extends Dropdown {
    constructor(id, data, {type='checkbox', placeholder='', default_value='[]'} = {}) {
        super(id, data, {type: type, placeholder: placeholder, default_value: default_value});
    }

    set_value(value) {
        value = JSON.parse(value);
        super.set_value(value);
    }

    update_value() {
        super.update_value();
        this.value = JSON.stringify(this.value);
        this.element.trigger(":change");
    }
}


class MultiLevelDropdown extends Dropdown {
    constructor(id, data, {type='checkbox', placeholder='', default_value=[]} = {}) {
        super(id, data, {type: type, placeholder: placeholder, default_value});
    }

    select(option, e) {
        var sub_option = $(e.target).closest('.sub-option'); // may not exist
        if (this.type == 'checkbox') {
            var option_checkbox = $(option).find('input').first();
            if (sub_option.length) {
                var sub_checkbox = sub_option.find('input')
                if (e.target.type != 'checkbox') {
                    sub_checkbox.prop("checked", !sub_checkbox.prop("checked"));
                }
                // Check if sub-options are now all selected
                var all_checked = true;
                $(option).find('.sub-option').each(function() {
                    if (!($(this).find('input').is(":checked"))) {
                        all_checked = false;
                    }
                });
                if (all_checked) {
                    option_checkbox.prop("checked", true);
                } else {
                    option_checkbox.prop("checked", false);
                }
            } else {
                if (e.target.type != 'checkbox') {
                    option_checkbox.prop("checked", !option_checkbox.prop("checked"));
                }
                if (option_checkbox.is(":checked")) {
                    $(option).find('input').prop("checked", true);
                } else {
                    $(option).find('input').prop("checked", false);
                }
            }
        } else if (this.type == 'radio') {
            this.element.find('input').prop("checked", false);
            if (sub_option.length) {
                sub_option.find('input').prop("checked", true);
            } else {
                $(option).find('input').first().prop("checked", true);
            }
        }
        this.update_value();
    }

    update_value() {
        var dropdown = this;
        var value_element = this.element.find('.value').first();
        this.value = [];
        this.element.find('input').each(function() {
            if ($(this).is(':checked')) {
                // Only take value if it is a sub-option or has no sub-options
                if ($(this).parent().hasClass('.sub-option') || $(this).parent().find('.sub-option').length == 0) {
                    dropdown.text = $(this).siblings('p').text();
                    dropdown.value.push($(this).val());
                }
            }
        });
        if (this.value.length > 1) {
            this.text = 'Multiple';
        } else if (this.value.length < 1) {
            this.text = this.placeholder;
        }
        value_element.text(this.text);
        this.element.trigger(":change");
    }

    styles() {
        var max_sub_height = 0;
        var dropdown_obj = this;
        this.element.find('.option').each(function() {
            var height = dropdown_obj.hide_sub_wrapper.call(this);
            max_sub_height = (height>max_sub_height) ? height : max_sub_height;
            $(this).hover(dropdown_obj.show_sub_wrapper, dropdown_obj.hide_sub_wrapper);
        });
        var dropdown = this.element;
        var options = dropdown.find('.options');
        options.css('height', 'fit-content');
        var new_height = max_sub_height + options.height();
        options.height(new_height);
        dropdown.find('.options-wrapper').each(function() {
            $(this).css('top', '-' + $(this).css('height'));
        });
        this.hide();
    }

    show_sub_wrapper() {
        // this is .option element
        $(this).find('.sub-options').addClass('visible');
        $(this).find('.sub-options-wrapper').css('top', '0');
    }

    hide_sub_wrapper() {
        // this is .option element
        var sub_wrapper = $(this).find('.sub-options-wrapper');
        var height = sub_wrapper.css("height");
        sub_wrapper.css('top', '-' + height);
        $(this).find('.sub-options').removeClass('visible');
        return parseInt(height);
    }

    build() {
        var element = $('#' + this.id);
        var value = $('<p/>')
            .addClass('value')
            .text('Value');
        var pointer = $('<i/>')
            .addClass('pointer fas fa-caret-left');
        var show_wrapper = $('<a/>')
            .addClass('show-wrapper')
            .attr('href', "#");
        var options = $('<div/>')
            .addClass('options');
        var options_wrapper = $('<div/>')
            .addClass('options-wrapper');
        for (let i=0; i<this.data.length; i++) {
            var option_data = this.data[i];
            var option = $('<div/>')
                .addClass('option');
            var input = $('<input/>')
                .attr('type', this.type)
                .attr('value', option_data[1]);
            var option_text = $('<p/>')
                .text(option_data[0]);
            var sub_options = $('<div/>')
                .addClass('sub-options');
            var sub_options_wrapper = $('<div/>')
                .addClass('sub-options-wrapper')
            for (let j=0; j<option_data[2].length; j++) {
                var sub_option_data = option_data[2][j];
                var sub_option = $('<div/>')
                    .addClass('sub-option');
                var sub_input = $('<input/>')
                    .attr('type', this.type)
                    .attr('value', sub_option_data[1]);
                var sub_text = $('<p/>')
                    .text(sub_option_data[0]);
                sub_option.append(sub_input);
                sub_option.append(sub_text);
                sub_options_wrapper.append(sub_option);
            }
            sub_options.append(sub_options_wrapper);
            if (!(this.type == 'radio' && option_data[2].length > 0)) {
                option.append(input);
            } else {
                option.append($('<span/>').addClass('input-spacer'));
            }
            option.append(option_text);
            option.append(sub_options)
            options_wrapper.append(option)
        }
        options.append(options_wrapper);
        element.append(value);
        element.append(pointer);
        element.append(show_wrapper);
        element.append(options);
        return [value, pointer, show_wrapper, options]
    }
}


class Modal extends JqueryElement {
    constructor(id, {action_func=null, cancel_func=null, action_data=null, cancel_data=null, escapable=true, build_func=null} = {}) {
        super(id);
        this.modal_element = this.element.find('.modal');
        this.escapable = escapable;
        this.action_func = action_func;
        this.action_data = action_data;
        this.cancel_func = cancel_func;
        this.cancel_data = cancel_data;
        this.offset_height = 30;
        if (build_func) {
            build_func.call(this);
        }
        this.listeners();
        this.show();
    }

    check_submit(element, e) {
        if (e.which == 13) {
            this.element.find('.action.btn').trigger("click");
        }
    }


    listeners() {
        this.element.find('.btn').off("click");
        this.element.off("keypress");
        this.element.find('.cancel.btn').click({object: this, func: this.hide}, this.dispatch);
        this.element.find('.action.btn').click({object: this, func: this.hide}, this.dispatch);
        if (this.action_func) {
            this.element.find('.action.btn').click(this.action_data ,this.action_func);
        }
        if (this.cancel_func) {
            this.element.find('.cancel.btn').click(this.cancel_data ,this.cancel_func);
        }
        this.element.keypress({object: this, func: this.check_submit}, this.dispatch);
    }

    show() {
        this.element.addClass('visible');
        this.modal_element.addClass('show');
        if (this.escapable) {
            closeFunctions['.modal'] = this;
        }
    }

    hide() {
        this.modal_element.removeClass('show');
        this.element.removeClass('visible');
        if (this.escapable) {
            delete closeFunctions['.modal'];
        }
    }
}


class CustomForm extends JqueryElement {
    constructor(id, custom_fields, form_fields, field_prefix) {
        // custom_fields hash to custom field manager object
        // form_fields hash to field input type
        // field prefix for element lookup
        super(id);
        this.custom_fields = custom_fields;
        this.form_fields = form_fields;
        this.field_prefix = field_prefix;
        this.listeners();
    }

    set_data(data) {
    // Sets all fields of form to data object.
        for (const field in data) {
            if (this.custom_fields.hasOwnProperty(field)) {
                // must have set_value method
                // must trigger ":change" event to update form
                this.custom_fields[field].set_value(data[field]);
            } else {
                this.element.find('#' + this.field_prefix + field).val(data[field]);
            }
        }
    }

    update_form(element, e, extra_data) {
        var form_field = this.element.find('#' + this.field_prefix + extra_data['field_name']);
        form_field.val(extra_data['custom_object'].value);
    }

    erase_data() {
        var reset_data = {}
        for (const field in this.form_fields) {
            if (this.custom_fields.hasOwnProperty(field)) {
                reset_data[field] = this.custom_fields[field].default_value;
            } else if (this.form_fields[field] == 'text') {
                reset_data[field] = '';
            } else {
                reset_data[field] = [];
            }
        }
        this.set_data(reset_data);
    }


    listeners() {
        // custom fields on ":change" update form
        for (const field in this.custom_fields) {
            var custom_info = {'field_name': field, 'custom_object': this.custom_fields[field]};
            this.custom_fields[field].element.on(":change", {
                func: this.update_form, object: this, extra_data: custom_info
            }, this.dispatch);
        }
    }
}


class AutocompleteInput extends JqueryElement {
    constructor(id, url) {
        super(id);
        this.build();
        this.url = url;
        this.value = '';
        this.default_value = '';
        this.query_data = null;
        this.pending_xhr = null;
        this.xhr = null;
        this.input = this.element.find('input');
        this.loader = this.element.find('.loading');
        this.listeners();
    }

    set_value(value) {
        this.input.val(value);
        this.update_value();
    }

    update_value() {
        this.value = this.input.val();
        this.element.trigger(":change");
    }

    get_query_data() {
        data = {
            'q': this.input.val(),
        }
        this.query_data = data;
    }

    autocomplete_initiate(input, e, site_select) {
        this.loader.show();
        this.show();
        if (this.xhr) {
            this.xhr.abort();
        }
        if (this.pending_xhr) {
            clearTimeout(this.pending_xhr);
            this.pending_xhr = null;
        }
        var q = $(input).val();
        if (!q.length) {
            return this.hide();
        }
        this.get_query_data();
        this.pending_xhr = setTimeout(this.autocomplete_send, 200, this);
    }

    autocomplete_send(self) {
        this.pending_xhr = null;
        self.xhr = $.ajax({
            url: self.url,
            method: 'GET',
            data: self.query_data,
            context: self,
            success: self.autocomplete_receive,
        });
    }

    autocomplete_receive(data) {
        this.xhr = null;
        this.build_matches(data['results']);
        this.loader.hide();
    }

    autocomplete_select(match) {
        this.input.val($(match).attr("value"));
        this.update_value();
        this.hide();
    }

    show() {
        this.element.find('.autocomplete').addClass('visible');
        this.element.find('.matches-wrapper').addClass('show');
        closeFunctions['#' + this.id] = this;
    }

    hide() {
        this.element.find('.matches-wrapper').removeClass('show');
        this.element.find('.autocomplete').removeClass('visible');
        delete closeFunctions['#' + this.id]
    }

    listeners() {
        this.input.on("input", {func: this.autocomplete_initiate, object: this}, this.dispatch);
        this.input.change({func: this.update_value, object: this}, this.dispatch);
        this.match_listeners();
    }

    match_listeners() {
        this.element.find('.autocomplete a').click({func: this.autocomplete_select, object: this}, this.dispatch);
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
        this.match_listeners();
    }

    build() {
        var input = $('<input/>')
            .attr("type", "text");
        var loading = $('<div/>')
            .addClass('loading')
            .css("display", "none");
        var spinner_container = $('<div/>')
            .addClass('center');
        var loading_spinner = $('<div/>')
            .addClass('small spinner');
        var autocomplete_container = $('<div/>')
            .addClass("autocomplete");
        var matches_wrapper = $('<div/>')
            .addClass('matches-wrapper');
        var no_match_container = $('<div/>')
            .addClass('item no-match');
        var no_match = $('<p/>')
            .text("No Matches");
        var matches_container = $('<div/>')
            .addClass("matches");
        no_match_container.append(no_match);
        matches_wrapper.append(no_match_container);
        matches_wrapper.append(matches_container);
        spinner_container.append(loading_spinner);
        loading.append(spinner_container);
        autocomplete_container.append(matches_wrapper);
        autocomplete_container.append(loading);
        this.element.append(input);
        this.element.append(autocomplete_container);
    }
}

class LinkInput extends JqueryElement {
    constructor(id) {
        super(id);
        this.value = '[]';
        this.default_value = '[]';
        this.modal_id = "link_modal";
        this.modal_element = $('#' + this.modal_id);
        this.build();
        this.list = this.element.find('.links');
        this.listeners();
        this.modal = null;
    }

    set_value(value) {
        this.list.empty();
        value = JSON.parse(value);
        for (let i=0; i<value.length; i++) {
            this.build_item(value[i]);
        }
        this.update_value();
    }

    update_value() {
        var value = [];
        this.list.find('.link').each(function() {
            var item = $(this).children().first();
            var name = item.text();
            var url = item.attr("href");
            value.push([name, url]);
        });
        this.value = JSON.stringify(value);
        this.element.trigger(":change");
    }

    modal() {
        this.modal_element.find('input').val(''); // reset values if modal has been used
        this.modal = new Modal(this.modal_id, {action_func:this.dispatch, action_data:{object: this, func: this.add_link}});
    }

    add_link() {
        var url = this.modal.element.find('.link-url').val();
        var name = this.modal.element.find('.link-name').val();
        if (url == '') {
            return
        }
        if (url.slice(0,8) != "https://") {
            url = "https://" + url;
        }
        if (name == '') {
            name = url;
        }
        var item_info = [name, url]
        this.build_item(item_info);
        this.update_value();
    }

    delete_link(delete_btn) {
        $(delete_btn).closest('.link').remove();
        this.update_value();
    }

    build_item(item) {
        var container = $('<div/>')
            .addClass('link')
        var link = $('<a/>')
            .addClass("blacklink")
            .attr("href", item[1])
            .attr("target", "_blank")
            .text(item[0]);
        var delete_btn = $('<a/>')
            .attr("href", "#")
            .addClass('delete fas fa-times blacklink');
        container.append(link);
        container.append(delete_btn);
        this.list.append(container);
        this.item_listeners();
    }

    listeners() {
        this.element.find('.link-upload').click({object: this, func: this.modal}, this.dispatch);
    }

    item_listeners() {
        this.element.find('.delete').off("click");
        this.element.find('.delete').click({object: this, func: this.delete_link}, this.dispatch);
    }

    build() {
        var btn = $('<a/>')
            .attr("href", "#")
            .addClass("link-upload fas fa-link blacklink");
        var links_container = $('<div/>')
            .addClass("links");
        this.element.append(btn);
        this.element.append(links_container);
    }
}