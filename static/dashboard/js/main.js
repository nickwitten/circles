
function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}


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
    alert_elem = $('<div/>')
        .addClass('alert alert-' + type)
        .text(message);
    close_btn = $('<i/>')
        .addClass('close fas fa-times blacklink')
        .attr('data-dismiss', 'alert')
        .attr('aria-label','close');
    alert_elem.append(close_btn);
    $('.alert-container').append(alert_elem);
    alert_elem.delay(1500).fadeOut();
}

function makeQuery(queryDict) {
    var url = '?';
    var ii = 0;
    for (const key in queryDict) {
        url += (ii) ? '&' : '';
        if (Array.isArray(queryDict[key])) {
            for (let i = 0; i < queryDict[key].length; i++) {
                url += (i) ? '&' : '';
                url += key + '[]=' + queryDict[key][i].toString();
            }
            if (!queryDict[key].length) {
                url += key + '[]=';
            }
        } else {
            url += key + '=' + queryDict[key].toString();
        }
        ii++;
    }
    return url
}

function parseQuery(queryString) {
    var query = {};
	var queryString = (queryString[0] === '?') ? queryString.substr(1) : queryString;
    if (!queryString.length) {
        return query;
    }
    var pairs = queryString.split('&');
    for (var i = 0; i < pairs.length; i++) {
        var pair = pairs[i].split('=');
        var name = decodeURIComponent(pair[0]);
        var value = decodeURIComponent(pair[1] || '');
        if (name.slice(-2) == '[]') {
            name = name.slice(0, -2);
            if (query.hasOwnProperty(name)) {
                query[name].push(value);
            } else {
                query[name] = [value];
            }
        } else {
            query[name] = value;
        }
    }
    return query;
}



function arraysEqual(a, b) {
    if (a === b) return true;
    if (a == null || b == null) return false;
    if (a.length !== b.length) return false;
    a = a.slice().sort();
    b = b.slice().sort();
    for (var i = 0; i < a.length; ++i) {
        if (a[i] !== b[i]) return false;
    }
    return true;
}




function create_loading_object() {
    obj = {
        is_loading_internal: false,
        is_loading_listener: function(val) {},
        set is_loading(val) {
            this.is_loading_internal = val;
            this.is_loading_listener(val);
        },
        get is_loading() {
            return this.is_loading_internal;
        },
        register_listener: function(listener) {
            this.is_loading_listener = listener;
        },
    }
    return obj
}





// Returns:
// list of month days,
// current date in (year, month, day) or null if not in current view,
// view moment object
function getMonthDates(month_offset) {
    var current_date = moment().format('YYYY-MM-DD');
    var year = parseInt(current_date.slice(0,4));
    var month = parseInt(current_date.slice(5,7));
    var day = parseInt(current_date.slice(9));
    current_date = [year, month, day];
    var view = moment().add(month_offset, 'month');
    var view_moment = view.clone();
    var view_month = view.format('MMMM');
    var view_year = view.format('YYYY');
    var firstday_weekday = view.startOf('month').format('d');
    var lastday_weekday = view.endOf('month').format('d');
    var month_length = view.daysInMonth();
    var start_monthday = view.startOf('month').startOf('week').format('DD');
    var days = [];
    var i = 0;
    for (i; i<firstday_weekday; i++) {
        days.push(start_monthday++);
    }
    i = 0;
    for (i; i<month_length; i++) {
        days.push(i+1);
    }
    i = lastday_weekday;
    var j = 1;
    for (i; i < 6; i++) {
        days.push(j++);
    }
    return [days, current_date, view_moment];
}




function expandTitle(placeholder, selector) {
    if (!selector) {
        selector = '';
    }
    $(selector + ' .expanding_size').text($(selector + ' .expanding_input').val()); // Copy text to the span element
    if ($(selector + ' .expanding_input').val() == '') { // When expanding_input is empty
        $(selector + ' .expanding_size').text(placeholder); // Expand to see the placeholder
    }
}




class FormDataJSON extends FormData {
    toJSON() {
        var object = {};
        this.forEach((value, key) => {
            // Reflect.has in favor of: object.hasOwnProperty(key)
            if(!Reflect.has(object, key)){
                object[key] = value;
                return;
            }
            if(!Array.isArray(object[key])){
                object[key] = [object[key]];
            }
            object[key].push(value);
        });
        return object
    }
}




class JqueryElement {
    constructor(id, parent=null) {
        this.id = id;
        this.element = $('#' + id);
        this.parent = parent;
    }

    // Call a function from jquery event data
    dispatch(event) {
        var event_this = this;
        var extra_data = null;
        if (event.data.hasOwnProperty('extra_data')) {
            extra_data = event.data.extra_data;
        }
        event.data.func.call(event.data.object, event_this, event, extra_data);
    }

    // Return a callback function to call func from the given object
    callback(func, {callfrom=this, extra_data={}} = {}) {
        return function() {
            func.call(callfrom, extra_data);
        }
    }
}




class AjaxForm extends JqueryElement {
    constructor(id, url, {onload_func=null, success_func=null, invalid_func=null, parent=null} = {}) {
        super(id, parent);
        this.url = url;
        this.method = "POST";
        this.errorClass = ".invalid";
        this.onload = onload_func;
        this.success = success_func;
        this.invalid = invalid_func;
        this.form_element = null;
        this.submit_btn = null
    }

    load() {
        this.element.load(this.url, null, this.callback(this.on_load, {callfrom: this}));
    }

    on_load() {
        // Addback includes the element being called from
        this.form_element = this.element.find("form").addBack("form");
        this.submit_btn = this.element.find(".submit-btn");

        this.listeners();
        if (typeof(this.onload) === 'function') {
            this.onload();
        }
    }

    submit_form(event_object, event) {
        /** Submit the form, if there are multiple
         *  forms found within this element, a 
         *  json string will be sent to the backend
         *  with the keys being the form id
        **/
        event.preventDefault();
        var url = this.url;
        var button_url = $(event_object).attr("data-url")
        if (button_url !== undefined) {
            var url = button_url;
        }
        var data;
        var process_data;
        var content_type;
        var headers;
        if (this.form_element.length == 1) {
            var data = new FormData(this.form_element[0]);
            process_data = false;  // For sending dom elements false
            content_type = false;
            headers = {};
        } else  if (this.form_element.length > 1) {
            var data = {}
            for (var i=0; i<this.form_element.length; i++) {
                var form = $(this.form_element[i])
                var form_data = new FormDataJSON(form[0])
                data[form.attr("id").replace("_form", "")] = JSON.stringify(form_data);
            }
            process_data = true;  // For sending dom elements false
            content_type = 'application/x-www-form-urlencoded; charset=UTF-8';  // this is the default
            var csrftoken = $('[name = "csrfmiddlewaretoken"]').val();
            headers = {
                'X-CSRFToken': csrftoken,
            }
        } else {
            console.log("No Form Found");
            return
        }
        $.ajax({
            type: this.method,
            url: url,
            data: data,
            headers: headers,
            processData: process_data,
            contentType: content_type,
            context: this,
            beforeSend: function () {
                //this.submit_btn.prop("disabled", true);
            },
            success: function (response) {
                if ($(response).find(this.errorClass).length > 0) {
                    // Form is not valid, update it with errors
                    this.element.html(response);
                    this.on_load();
                    if (typeof(this.invalid) == 'function') {
                        this.invalid(response);
                    }
                } else if (typeof(this.success) === 'function') {
                    this.success(response);
                }
            }
        });
    }

    listeners() {
        this.element.find("*").addBack("*").off(".ajaxform");
        this.element.find(".submit-btn").on("click.ajaxform", {'func': this.submit_form, 'object': this}, this.dispatch);
        this.element.find(".delete-btn").on("click.ajaxform", {'func': this.submit_form, 'object': this}, this.dispatch);
    }
}




class ModelListEdit extends JqueryElement {
    constructor(id, datalist_id, form_id, parent) {
        super(id, parent)
        this.datalist_id = datalist_id;
        this.form_id = form_id;
        this.init_datalist();
        this.listeners();
    }

    init_datalist() {
        var list_elements = this.element.find('.list-item');
        var jquery_items = []
        for (var i=0; i<list_elements.length; i++ ) {
            jquery_items.push($(list_elements[i]));
        }
        this.data_list = new DataList(this.datalist_id, jquery_items, this);
        this.data_list.reset();
    }

    select_form(option) {
        if ($(option).attr("data-url")) {
            var onload_func = function() {
                this.parent.show_form();
            }
            var success_func = function(response) {
                this.parent.hide_form();
                var data_list = $('#'+this.parent.datalist_id);
                data_list.html($(response).find("#"+this.parent.datalist_id));
                this.parent.init_datalist();
                this.parent.listeners();
            }
            var invalid_func = function() {
                this.parent.add_back_btn();
                this.parent.listeners();
            }
            this.form = new AjaxForm(this.form_id, $(option).attr("data-url"), {'onload_func': onload_func, 'success_func': success_func, 'invalid_func': invalid_func, 'parent': this});
            this.form.load();
        }
    }

    show_form() {
        // (this) is the AjaxForm
        this.add_back_btn();
        var hidden = this.element.find(".content.hide");
        hidden.removeClass("hide");
        var full_width = hidden.css("width", "auto").width();
        hidden.width(0);
        hidden.width(full_width);
        this.listeners();
    }

    hide_form() {
        if (this.hasOwnProperty("form")) {
            this.form.element.css("width", "");
            this.form.element.addClass("hide");
        }
    }

    add_back_btn() {
        if (!$('#'+this.form_id).find('.back').length) {
            $('#'+this.form_id).prepend($('<i/>').addClass("back fas fa-times blacklink"));
        }
    }

    listeners() {
        this.element.find("*").addBack("*").off(".list-edit");
        this.element.find(".option").on("click.list-edit", {'object': this, 'func': this.select_form}, this.dispatch);
        this.element.find(".back").on("click.list-edit", {'object': this, 'func': this.hide_form}, this.dispatch);
        this.element.find(".list-item").on("click.list-edit", {'object': this, 'func': this.select_form}, this.dispatch);
    }
}




class DataList extends JqueryElement {
    constructor(id, items, parent) {
        super(id, parent);
        this.element.addClass('data-list');
        this.items = (items) ? items : [];
        this.default_item_ct = 14;
    }

    reset() {
        this.empty();
        this.build();
        this.alternatingStyle();
    }

    alternatingStyle() {
        var children = this.element.children();
        for (var i=0; i<children.length; i++) {
            if (i % 2) {
                $(children[i]).addClass('shaded')
            }
        }
    }

    empty() {
        this.element.empty();
    }

    build() {
        var item_min_height = 0;
        if (this.items.length) {
            for (var i=0; i<this.items.length; i++) {
                var item = this.items[i].height('auto');
                this.element.append(item);
                var height = item.outerHeight(true);
                item_min_height = (height>item_min_height) ? height : item_min_height;
            }
            this.empty();
        } else  {
            item_min_height = this.element.height() / this.default_item_ct;
        }
        this.element.empty();
        var items_on_screen = Math.floor(this.element.outerHeight(true)/item_min_height);
        var item_size = (this.element.outerHeight(true)) / items_on_screen;
        for (var i=0; i<this.items.length; i++) {
            this.element.append(this.items[i])
        }
        var item_ct = this.element.children().length;
        if (item_ct < items_on_screen) {
            for (var i=0; i<(items_on_screen-item_ct); i++) {
                this.element.append($('<div/>'));
            }
        }
        this.element.children().each(function() {
            var mpHeight = $(this).outerHeight(true)-$(this).height();  // margin/padding
            $(this).height(item_size-mpHeight);
        });
    }
}


class Folders extends JqueryElement {
    constructor(id, parent=null) {
        super(id, parent);
        this.max_height = 550;
        this.listeners();
    }

    open(header_element) {
        var folder = $(header_element).closest('.folder');
        var content = folder.find('.folder-content');
        var height = content.height('auto').outerHeight(true);
        if (this.max_height !== null) {
            height = (height<this.max_height)?height:this.max_height
        }
        content.height(0);
        content.height(height+2);
        folder.addClass("open");
    }

    close(header_element) {
        var folder = $(header_element).closest('.folder');
        var content = folder.find('.folder-content');
        content.height(0);
        folder.removeClass("open");
    }

    toggle(header_element, e, event_this) {

        if ($(e.target).is('input')) {
            return
        }

        var folder = $(header_element).closest('.folder');
        var content = folder.find('.folder-content');
        if (folder.hasClass("open")) {
            this.close(header_element);
        } else {
            this.open(header_element);
        }
    }

    listeners() {
        this.element.find("*").off(".folder");
        this.element.find(".folder-header").on("click.folder", {'object': this, 'func': this.toggle}, this.dispatch);
    }
}


class Dropdown extends JqueryElement {
    constructor(id, data, {type='checkbox', placeholder='', value_id='.option input', default_value=[], parent=null} = {}) {
        super(id, parent);
        this.data = data;
        this.type = type;
        this.placeholder = placeholder;
        this.default_value = default_value;
        this.value_id = value_id;
        this.value = default_value;
        this.val_to_text = {}; // Hash values to display text
        this.text = '';
        this.detail = false;
        this.initialize();
    }

    initialize() {
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
        if (!this.detail) {
            dropdown.find('.show-wrapper').show();
        }
        // Stop checking for clicks outside
        delete closeFunctions['#' + this.id + ' .option'];
    }

    set_value(values) {
        if (!Array.isArray(values )) {
            values = [values];
        }
        // Uncheck all
        this.element.find('input').prop("checked", false);
        this.element.find('.value').first().text(this.placeholder);
        // Check if matches a value
        for (let i=0; i<values.length; i++) {
            var value = values[i];
            var dropdown = this;
            this.element.find(this.value_id).each(function() {
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
            this.update_value();
            this.hide();
        } else if (this.type == 'checkbox') {
            // Check if it's already been changed
            if (e.target.type != 'checkbox') {
                var input = $(option).find('input');
                input.prop("checked", !input.prop("checked"));
            }
            this.update_value();
        }
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

    set_detail() {
        this.detail = true;
        this.element.addClass('detail');
    }

    set_update() {
        this.detail = false;
        this.element.removeClass('detail');
        this.styles();
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
        this.element.empty();
        this.val_to_text = {};
        var value = $('<p/>')
            .addClass('value')
        var pointer = $('<i/>')
            .addClass('pointer fas fa-caret-left');
        var show_wrapper = $('<span/>')
            .addClass('show-wrapper');
        var options = $('<div/>')
            .addClass('options');
        var options_wrapper = $('<div/>')
            .addClass('options-wrapper');
        for (let i=0; i<this.data.length; i++) {
            var option_data = this.data[i];
            this.val_to_text[option_data[1]] = option_data[0];
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
        this.element.append(value);
        this.element.append(pointer);
        this.element.append(show_wrapper);
        this.element.append(options);
        return [value, pointer, show_wrapper, options]
    }
}


class JsonDropdown extends Dropdown {
    constructor(id, data, {type='checkbox', placeholder='', default_value='[]', parent=null} = {}) {
        super(id, data, {type: type, placeholder: placeholder, default_value: default_value, parent: parent});
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
    constructor(id, data, {type='checkbox', placeholder='', value_id='.sub-option input', default_value=[], parent=null} = {}) {
        super(id, data, {type: type, placeholder: placeholder, value_id: value_id, default_value: default_value, parent:parent});
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
        var old_value = this.value;
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
        if (!arraysEqual(old_value, this.value)) {
            this.element.trigger(":change");
        }
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
        this.element.empty();
        var value = $('<p/>')
            .addClass('value')
            .text('Value');
        var pointer = $('<i/>')
            .addClass('pointer fas fa-caret-left');
        var show_wrapper = $('<span/>')
            .addClass('show-wrapper')
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
                this.val_to_text[sub_option_data[1]] = sub_option_data[0];
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
        this.element.append(value);
        this.element.append(pointer);
        this.element.append(show_wrapper);
        this.element.append(options);
        return [value, pointer, show_wrapper, options]
    }
}




class ObjectSelect extends Dropdown {
    constructor(id, data, field_id, {object_url=null, type='checkbox', placeholder='', default_value=[], parent=null} = {}) {
        super(id, data, {type:type, placeholder:placeholder, default_value:default_value, parent:parent});
        this.form_field = $('#' + field_id);
        this.object_url = object_url;
        this.initialize();
    }

    initialize() {
        super.initialize();
        if (this.form_field) {
            this.update_form_field_options();
        }
    }

    update_form_field_options() {
        this.form_field.empty();
        for (let i=0; i<this.data.length; i++) {
            var option = $('<option/>')
                .text(this.data[i][0])
                .val(this.data[i][1]);
            if (this.value.includes(this.data[i][1])) {
                option.prop('selected', true);
            }
            this.form_field.append(option);
        }
    }

    update_select() {
        if (this.form_field) {
            this.update_form_field_options();
        }
        this.build();
        this.styles();
        this.listeners();
        this.update_display();
    }

    update_display() {
        var select = this;
        this.element.find('.object-list').empty();
        var text = '';
        this.element.find('input').each(function() {
            if (select.value.includes(parseInt($(this).val())) || select.value.includes($(this).val())) {
                $(this).prop('checked', true);
                text = $(this).siblings('p').text();
                select.build_object([text, $(this).val()]);
            } else {
                $(this).prop('checked', false);
            }
        });
        var value_text = this.element.find('.value').first();
        this.element.children().addClass('half');
        if (this.value.length > 1) {
            text = 'Multiple';
        } else if (this.value.length < 1) {
            this.element.children().removeClass('half');
            text = this.placeholder;
        }
        value_text.text(text);
        this.element.trigger(':update');
    }

    set_value(value) {
        this.value = value;
        this.update_display();
    }

    select(option, e) {
        super.select(option, e);
        this.update_display();
    }

    get_object_url(object_info) {
        if (this.object_url) {
            return this.object_url + object_info[1].toString();
        }
        return "#"
    }

    build_object(object_info) {
        var object_container = $('<div/>')
            .addClass('object-container');
        var object = $('<a/>')
            .text(object_info[0])
            .addClass('object blacklink');
        var url = this.get_object_url(object_info)
        object.attr("href", url);
        object_container.append(object);
        this.element.find('.object-list').append(object_container);
    }

    build() {
        this.element.empty();
        this.element.append($('<div/>').addClass('object-list'));
        this.element.append($('<div/>').addClass('dropdown'))
        this.element = this.element.find('.dropdown');
        super.build();
        this.element = this.element.closest('.object-select');
    }
}




class MultiLevelObjectSelect extends MultiLevelDropdown {
    constructor(id, data, field_id, {object_url=null, type='checkbox', placeholder='', default_value=[], parent=null} = {}) {
        super(id, data, {type:type, placeholder:placeholder, default_value:default_value, parent:parent});
        this.form_field = $('#' + field_id);
        this.object_url = object_url;
        this.initialize();
    }

    initialize() {
        super.initialize();
        if (this.form_field) {
            this.update_form_field_options();
        }
    }

    update_form_field_options() {
        this.form_field.empty();
        for (let i=0; i<this.data.length; i++) {
            var theme = this.data[i];
            var modules = theme[2];
            if (!modules) {
                continue
            }
            for (let j=0; j<modules.length; j++) {
                var option_data = modules[j];
                var option = $('<option/>')
                    .text(option_data[0])
                    .val(option_data[1]);
                if (this.value.includes(option_data[1])) {
                    option.prop('selected', true);
                }
                this.form_field.append(option);
            }
        }
    }

    update_select() {
        if (this.form_field) {
            this.update_form_field_options();
        }
        this.build();
        this.styles();
        this.listeners();
        this.update_display();
    }

    update_display() {
        var select = this;
        this.element.find('.object-list').empty();
        var text = '';
        this.element.find('.option').each(function() {
            var all_checked = true;
            var sub_options = $(this).find('.sub-options').find('input');
            sub_options.each(function() {
                if (select.value.includes(parseInt($(this).val())) || select.value.includes($(this).val())) {
                    $(this).prop('checked', true);
                    text = $(this).siblings('p').text();
                    select.build_object([text, $(this).val()]);
                } else {
                    all_checked = false;
                    $(this).prop('checked', false);
                }
            });
            if (all_checked && sub_options.length) {
                $(this).find('input').first().prop('checked', true);
            }
        });
        var value_text = this.element.find('.value').first();
        this.element.children().addClass('half');
        if (this.value.length > 1) {
            text = 'Multiple';
        } else if (this.value.length < 1) {
            this.element.children().removeClass('half');
            text = this.placeholder;
        }
        value_text.text(text);
        this.element.trigger(':update');
    }

    set_value(value) {
        this.value = value;
        this.update_display();
        this.element.trigger(':update');
    }

    select(option, e) {
        var sub_options = $(option).find('.sub-option');
        if ($(option).hasClass('option') && !sub_options.length) {
             $(option).find('input').prop('checked', false);
            return
        }
        super.select(option, e);
        this.update_display();
    }

    get_object_url(object_info) {
        if (this.object_url) {
            return this.object_url + object_info[1].toString();
        }
        return "#"
    }


    build_object(object_info) {
        var object_container = $('<div/>')
            .addClass('object-container');
        var object = $('<a/>')
            .text(object_info[0])
            .addClass('object blacklink');
        var url = this.get_object_url(object_info);
        object.attr("href", url);
        object_container.append(object);
        this.element.find('.object-list').append(object_container);
    }

    build() {
        this.element.empty();
        this.element.append($('<div/>').addClass('object-list'));
        this.element.append($('<div/>').addClass('multi-level-dropdown'))
        this.element = this.element.find('.multi-level-dropdown');
        super.build();
        this.element = this.element.closest('.object-select');
    }
}




class Modal extends JqueryElement {
    constructor(id, {action_func=null, cancel_func=null, action_data=null, cancel_data=null, escapable=true, build_func=null} = {}) {
        super(id);
        this.modal_element = this.element.find('.modal');
        this.escapable = escapable;
        this.build_func = build_func;
        this.action_func = action_func;
        this.action_data = action_data;
        this.cancel_func = cancel_func;
        this.cancel_data = cancel_data;
        this.offset_height = 30;
        if (this.build_func) {
            this.build_func.call(this);
        }
        this.show();
        this.listeners();
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
        this.element.trigger(":hide");
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
            } else if (this.form_fields.hasOwnProperty(field)) {
                this.element.find('#' + this.field_prefix + field).val(data[field]);
            }
        }
        this.element.trigger(':change');
    }

    update_form(element, e, extra_data) {
        var form_field = this.element.find('#' + this.field_prefix + extra_data['field_name']);
        form_field.val(extra_data['custom_object'].value);
        this.element.trigger(':change');
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
        var form = this
        for (const field in this.form_fields) {
            if (this.custom_fields.hasOwnProperty(field)) {
                var custom_info = {'field_name': field, 'custom_object': this.custom_fields[field]};
                this.custom_fields[field].element.on(":change", {
                    func: this.update_form, object: this, extra_data: custom_info
                }, this.dispatch);
            } else {
                $('#' + this.field_prefix + field).change(function() {
                    form.element.trigger(':change');
                });
            }
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
        this.element.find('.autocomplete p').click({func: this.autocomplete_select, object: this}, this.dispatch);
    }

    build_matches(data) {
        this.element.find('.matches').empty();
        for (let i=0; i<data.length; i++) {
            var match_container = $('<div/>')
                .addClass("match")
                .addClass("item");
            var match = $("<p/>")
                .text(data[i][0])
                .attr("value", data[i][1])
                .addClass("blacklink");
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
        this.element.empty();
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

class FileInput extends JqueryElement {

    constructor(id) {
        super(id);
        this.input_id = id.replace('input', 'upload')
        this.value = [];
        this.default_value = [];
        this.delete_files = [];
        this.build();
        this.list_element = this.element.find('.files');
        this.input_element = this.element.find('input');
        this.update_value();
        this.listeners();
    }

    set_value(value) {
        this.delete_files = [];
        this.input_element.val('');
        this.list_element.empty();
        for (let i=0; i<value.length; i++) {
            this.build_item(value[i]);
        }
        this.form_data = new FormData()
    }

    update_value() {
        this.list_element.find('.file').each(function() {
            if ($(this).find('.delete').length == 0) {
                $(this).remove();
            }
        });
        var files = this.input_element[0].files;
        this.form_data = new FormData()
        for (let i=0; i<files.length; i++) {
            this.build_item([files[i].name, 0, '#']);
            this.form_data.append(files[i].name, files[i]);
        }
	this.element.trigger(':change');
    }

    set_detail() {
        this.element.find('.file-upload').hide();
        this.element.find('i').hide();
    }

    set_update() {
        this.element.find('.file-upload').show();
        this.element.find('i').show();
    }

    delete_file(delete_btn) {
        this.delete_files.push($(delete_btn).attr("value"));
        $(delete_btn).closest('.file').remove();
        this.element.trigger(':change');
    }

    item_listeners() {
        this.element.find('.delete').off("click");
        this.element.find('.delete').click({object: this, func: this.delete_file}, this.dispatch);
    }

    build_item(item) {
        var container = $('<div/>')
            .addClass('file')
        var link = $('<a/>')
            .addClass("blacklink")
            .attr("href", item[2])
            .attr("target", "_blank")
            .text(item[0]);
        var delete_btn = $('<i/>')
            .addClass('delete fas fa-times blacklink')
            .attr("value", item[1]);
        container.append(link);
        if (item[1]) {
            container.append(delete_btn);
        }
        this.list_element.append(container);
        this.item_listeners();
    }


    build() {
        var input = $('<input/>')
            .attr("id", this.input_id)
            .prop("multiple", true)
            .attr("type", "file");
        var btn = $('<label/>')
            .attr("for", this.input_id)
            .addClass("file-upload fas fa-file-upload blacklink");
        var links_container = $('<div/>')
            .addClass("files");
        this.element.append(input);
        this.element.append(btn);
        this.element.append(links_container);
    }

    listeners() {
        this.input_element.change({object: this, func: this.update_value}, this.dispatch);
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

    set_detail() {
        this.element.find('.link-upload').hide();
        this.element.find('i').hide();
    }

    set_update() {
        this.element.find('.link-upload').show();
        this.element.find('i').show();
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
        var delete_btn = $('<i/>')
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
        var btn = $('<i/>')
            .addClass("link-upload fas fa-link blacklink");
        var links_container = $('<div/>')
            .addClass("links");
        this.element.append(btn);
        this.element.append(links_container);
    }
}



class DatePicker extends JqueryElement{

    constructor(id) {
        super(id);
        this.month_offset = 0;
        this.content = this.element.find('.dates-container');
        this.value = '';
        this.listeners();
        this.hide();  // add listener to show
    }

    set_value(val) {
        this.value = val;
        this.update_value();
    }

    set_detail() {
        this.element.find('.date-select-btn').addClass('inactive');
        this.element.find('.show-wrapper').hide();
    }

    set_update() {
        this.element.find('.date-select-btn').removeClass('inactive');
        this.element.find('.show-wrapper').show();
    }

    update_value() {
        var year = this.value.slice(0,4);
        var month = this.value.slice(5,7);
        var day = this.value.slice(8);
        this.element.find('.value').text([month, day, year].join('/'));
        this.element.trigger(":change");
    }

    show() {
        this.show_month();
        this.element.addClass('shadow');
        this.element.find('.select-container').addClass('visible');
        this.element.find('.date-select').addClass('show');
        this.element.find('.show-wrapper').off('click');
        closeFunctions['.date-select'] = this;
    }

    hide() {
        this.element.removeClass('shadow');
        this.element.find('.select-container').removeClass('visible');
        this.element.find('.date-select').removeClass('show');
        this.listeners();
        delete closeFunctions['.date-select'];
    }

    show_month() {
        this.content.empty();
        var dates = getMonthDates(this.month_offset);
        var month_v = dates[2].format('MMMM');
        var month = dates[2].format('MM');
        var year = dates[2].format('YYYY');
        dates = dates[0];
        this.element.find('.month').text(month_v);
        this.element.find('.month').attr('data-number', month);
        this.element.find('.year').text(year);
        this.element.find('.value').text()
        for (var i=0; i<(dates.length/7); i++) {
            // check if the date has been selected
            var selected = []
            var inactive = []
            for (var j=0; j<7; j++) {
                var month_str = month;
                var day = dates[i*7+j].toString();
                day = (day.length == 1) ? '0'+day : day;
                if (i==0 && parseInt(day) > 7) {
                    month_str = (parseInt(month)-1).toString();
                    inactive.push(j);
                } else if (i==(dates.length/7-1) && parseInt(day) < 7) {
                    month_str = (parseInt(month)+1).toString();
                    inactive.push(j);
                }
                var date = [year, month, day].join('-');
                if (this.value.includes(date) && !inactive.includes(j)) {
                    selected.push(j)
                };
            }
            this.build_week(dates.slice(i*7,i*7+7), selected, inactive);
        }
        this.item_listeners();
    }

    select_date(day_element) {
        var day = $(day_element).children().text()
        day = (day.length < 2) ? '0'+day : day; // zero pad
        var month = this.element.find('.month').attr('data-number');
        var year = this.element.find('.year').text();
        var date = [year, month, day].join('-');

        if (!$(day_element).hasClass('selected')) {
            this.value = date;
        }
        this.show_month();
        this.update_value();
    }

    next_month() {
        this.month_offset++;
        this.show_month();
    }

    previous_month() {
        this.month_offset--;
        this.show_month();
    }

    build_week(days, selected, inactive) {
        var container = $('<div/>').addClass('container');
        var week = $('<ul/>')
            .addClass('calendar-week');
        for (var i=0; i<days.length; i++) {
            /////// Day Box HTML /////////
            var day = $('<li/>')
            if (inactive.includes(i)) {
                var classlist = 'calendar-day inactive';
            } else {
                var classlist = 'calendar-day';
            }
            if (selected.includes(i)) {
                classlist += ' selected';
            }
            day = day.addClass(classlist);
            ///// Month Number HTML //////
            var day_monthnum = $('<p/>')
                .text(days[i])
                .addClass('monthnum');
            day.append(day_monthnum);
            week.append(day);
        }
        container.append(week);
        this.content.append(container);
    }

    item_listeners() {
        this.element.find('.calendar-day').off("click");
        this.element.find('.calendar-day').click({func: this.select_date, object: this}, this.dispatch);
        this.element.find('.calendar-day.inactive').off("click");
    }

    listeners() {
        var events = 'click';
        this.element.off(events);
        this.element.find('*').off(events);
        this.element.find('.show-wrapper').click({func: this.show, object: this}, this.dispatch);
        this.element.find('.next').click({func: this.next_month, object: this}, this.dispatch);
        this.element.find('.previous').click({func: this.previous_month, object: this}, this.dispatch);
    }
}




class MultiDatePicker extends DatePicker {
    constructor(id) {
        super(id);
        this.default_value = [];
        this.value = this.default_value;
    }

    select_date(day_element) {
        var day = $(day_element).children().text()
        day = (day.length < 2) ? '0'+day : day; // zero pad
        var month = this.element.find('.month').attr('data-number');
        var year = this.element.find('.year').text();
        var date = [year, month, day].join('-');

        if ($(day_element).hasClass('selected')) {
            $(day_element).removeClass('selected');
            this.value.splice(this.value.indexOf(date), 1);
        } else  {
            this.value.push(date);
        }
        this.show_month();
        // Update date displayed
        if (this.value.length > 1) {
            this.element.find('.value').text('Multiple');
            this.element.trigger(":change"); // change not handled by update_value
        } else if (this.value.length == 1) {
            day = this.element.find('.selected').children().text();
            day = (day.length < 2) ? '0'+day : day;
            this.element.find('.value').text([month, day, year].join('/'));
            this.update_value();
        }
    }

    update_value() {
        var date = this.value[0];
        var year = date.slice(0,4);
        var month = date.slice(5,7);
        var day = date.slice(8);
        this.element.find('.value').text([month, day, year].join('/'));
        this.element.trigger(":change");
    }
}




class TimePicker extends JqueryElement {
    constructor(id) {
        super(id);
        this.default_value = ["12:00:00", "12:00:00"];
        this.value = this.default_value;
        this.update_value();
        this.listeners();
    }

    update_value() {
        for (let i=0; i<this.value.length; i++) {
            var time_str = this.value[i];
            var time_array = time_str.split(':');
            var hour = parseInt(time_array[0]);
            var minute = parseInt(time_array[1]);
            var period = (hour >= 12 ) ? 'p.m.' : 'a.m.';
            hour = (hour > 12) ? hour - 12 : hour;
            hour = (hour == 0) ? 12 : hour;
            minute = (minute == 0) ? '00' : minute;
            var id = (i==0) ? 'p.start' : 'p.end';
            this.element.find(id + '-hour').text(hour.toString());
            this.element.find(id + '-minute').text(minute.toString());
            this.element.find(id + '-period').text(period);
        }
        this.element.trigger(":change");
    }

    change_time(btn) {
        var classList = btn.classList;
        var id = classList[0];
        if (id.includes('hour')) {
            var time_ind = 0;
            var time_difference = 1;
            var time_step = 1;
            var time_limits = [0, 23];
        } else if (id.includes('minute')) {
            var time_ind = 1;
            var time_difference = 10;
            var time_step = 10;
            var time_limits = [0, 50];
        } else if (id.includes('period')) {
            var time_ind = 0;
            var time_difference = 12;
            var time_step = 1;
            var time_limits = [0, 23];
        }
        var value_ind = (id.includes('start')) ? 0 : 1;
        var time_array = this.value[value_ind].split(':');
        var current_time = parseInt(time_array[time_ind]);
        current_time += (classList[2].includes('up')) ? time_difference : -time_difference;
        if (current_time < time_limits[0]) {
            current_time = time_limits[1] - (time_limits[0] - current_time) + time_step;
        } else if (current_time > time_limits[1]) {
            current_time = time_limits[0] + (current_time - time_limits[1]) - time_step;
        }
        current_time = (current_time == 0) ? '00' : current_time;
        time_array[time_ind] = current_time.toString();
        this.value[value_ind] = time_array.join(':');
        this.update_value();
    }

    set_value(value, start=true, end=true) {
        if (start && end) {
            this.value = value;
        } else if (start) {
            this.value[0] = value;
        } else if (end) {
            this.value[1] = value;
        }
        this.update_value();
        this.element.trigger(":change");
    }

    set_detail() {
        this.element.find('i').addClass('inactive');
    }

    set_update() {
        this.element.find('i').removeClass('inactive');
    }

    listeners() {
        this.element.find('.fas.fa-angle-up').click({func: this.change_time, object: this}, this.dispatch);
        this.element.find('.fas.fa-angle-down').click({func: this.change_time, object: this}, this.dispatch);
    }
}



class Menu extends JqueryElement {

    constructor(id, menu_btn_id) {
        super(id);
        this.menu_btn = $('#' + menu_btn_id);
        this.listeners();
    }

    show() {
        this.element.addClass('show');
        closeFunctions['#' + this.id] = this;
    }

    hide() {
        this.element.removeClass('show');
        delete closeFunctions['#' + this.id];
    }

    listeners() {
        this.menu_btn.click({func: this.show, object: this}, this.dispatch);
        this.element.find('.back').click({func: this.hide, object: this}, this.dispatch);
    }
}



class MenuSiteSelect extends Folders {
    constructor(id, type, parent=null) {
        super(id, parent);
        this.value = [];
        this.type = type;
        this.reset();
        if (type == 'radio')  // One must be chosen for radio button
        {
            this.select(this.element.find('.site')[0]);
        }
        this.listeners();
    }

    update_value() {
        this.value = [];
        var site_select = this;
        this.element.find('.site input').each(function() {
            if ($(this).is(':checked')) {
                site_select.value.push($(this).val());
            }
        });
    }

    change(selected, e) {
        this.select(selected, e);
        this.element.trigger(':change');
    }

    set_value(val, change) {
        if (Array.isArray(val) && Array.isArray(this.value) && arraysEqual(this.value, val)) {
            change = false;
        }
        if (this.value == val) {
            change = false;
        }
        this.value = val;
        if (!Array.isArray(val)) {
            val = [val];
        }
        var site_select = this;
        var all_chapters = true;
        this.element.find('.chapter').siblings().each(function() {
            var all_sites = true;
            $(this).find('.site input').each(function() {
                if (val.includes($(this).val())) {
                    $(this).prop('checked', true);
                } else {
                    $(this).prop('checked', false);
                    all_sites = false;
                }
            });
            if (all_sites) {
                $(this).siblings('.chapter').children('input').first().prop('checked', true);
                console.log(this);
            } else {
                $(this).children('input').first().prop('checked', false);
                all_chapters = false;
            }
        });
        if (all_chapters) {
            this.element.find('.all input').prop('checked', true);
        }
        if (change) {
            this.element.trigger(':change');
        }
    }

    select(selected, e) {
        // if (!$(selected).is('input')) {
        //     $(selected).find('input').prop("checked", true);
        // }
        var option = $(selected).closest('div').addBack();
        var option_input = option.find('input');
        console.log(option);
        console.log(option_input);
        console.log(option_input.prop("checked"));

        if (this.type == 'radio') {
            this.element.find('input').each(function() {
                $(this).prop("checked", false);
            });
            option_input.prop("checked", true);
            this.update_value();
            return
        }

        if (!e || !$(e.target).is('input')) {
            // if (e !== undefined) {
            //     option_input = $(e.target);
            // }
            console.log(option_input.prop("checked"));
            option_input.prop('checked', !(option_input.prop("checked")));
            console.log(option_input.prop("checked"));
        }

        // ALL was selected
        if (option.hasClass('all')) {
            console.log(option_input.prop("checked"));
            this.element.find('input').each(function() {
                $(this).prop('checked', option_input.prop("checked"));
            });
        }

        // Full chapter was selected
        if (option.hasClass('chapter')) {
            console.log(option_input.prop("checked"));
            option.siblings().find('input').each(function() {
                $(this).prop('checked', option_input.prop("checked"));
            });
        }

        // Site was selected
        if (option.hasClass('site')) {
            var allChecked = true;
            option.siblings('.site').addBack().each(function() {
                if (!($(this).find('input').is(':checked'))) {
                    allChecked = false;
                }
            });
            option.closest('.folder').find('.chapter').find('input').prop('checked', allChecked);
        }

        // Check to see if all chapters are selected
        allChecked = true
        this.element.find('.chapter').siblings().each(function() {
            $(this).children().find('input').each(function() {
                console.log(this);
                if (!$(this).prop("checked")) {
                    allChecked = false;
                }
            })
        });
        console.log(allChecked);
        this.element.find('.all input').prop('checked', allChecked);
        this.update_value();
    }

    show() {
        this.element.addClass('show');
        closeFunctions['#' + this.id] = this;
    }

    hide() {
        this.element.removeClass('show');
        delete closeFunctions['#' + this.id];
    }

    reset() {
        this.element.find('input').each(function() {
            $(this).prop('checked', false);
        });
    }

    listeners() {
        super.listeners();
        this.element.find("*").addBack("*").off(".menu");
        $('#menu_btn').on("click.menu", {func: this.show, object: this}, this.dispatch);
        this.element.find('.back').on("click.menu", {func: this.hide, object: this}, this.dispatch);
        //this.element.find('.chapter').siblings().addBack().find('input').on("click.menu", {func: this.change, object: this}, this.dispatch);
        this.element.find('.site').on("click.menu", {func: this.change, object: this}, this.dispatch);
        this.element.find('.chapter input').on("click.menu", {func: this.change, object: this}, this.dispatch);
    }
}




class ColorPicker extends JqueryElement {
    constructor(id, default_value='hsla(0.0, 93%, 64%, 0.3)') {
        super(id);
        this.styles();
        this.select(this.element.find('.color').first());
        this.close_selector = '.color-select';
        this.default_value = default_value;
        this.value = this.default_value;
        this.listeners();
    }

    show() {
        this.element.find('.colors').addClass("visible");
        this.element.find('.colors-wrapper').addClass("show");
        closeFunctions[this.close_selector] = this;
    }

    hide() {
        this.element.find('.colors').removeClass("visible");
        this.element.find('.colors-wrapper').removeClass("show");
        delete closeFunctions[this.close_selector];
    }

    toggle() {
        if (this.element.find('.colors-wrapper').hasClass('show')) {
            this.hide();
        } else {
            this.show();
        }
    }

    select(color) {
        color = $(color).attr('data-color');
        this.element.css('background-color', color.slice(0,20) + '0.7');
        this.value = color;
        this.element.trigger(":change");
    }

    set_detail() {
        this.element.find('.show-wrapper').hide();
    }

    set_update() {
        this.element.find('.show-wrapper').show();
    }

    styles() {
        $('.color').each(function() {
            var color = $(this).attr('data-color');
            var bold_color = color.slice(0, 20) + '0.7)';
            $(this).css('background-color', bold_color);
        });
    }

    set_value(value) {
        var color_picker = this;
        $('.color').each(function() {
            if ($(this).attr('data-color') == value) {
                color_picker.select(this);
            }
        });
    }

    listeners() {
        this.element.find('.show-wrapper').click({func: this.toggle, object: this}, this.dispatch);
        this.element.find('.color').click({func: this.select, object: this}, this.dispatch);
    }
}
