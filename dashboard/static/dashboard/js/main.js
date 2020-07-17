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
    dispatch(event) {
        var event_this = this;
        event.data.func.call(event.data.object, event_this, event);
    }
}

class Dropdown extends JqueryElement {
    constructor(id, data, type, placeholder) {
        super();
        this.id = id;
        this.element = $('#' + this.id);
        this.data = data;
        this.type = type;
        this.placeholder = placeholder;
        this.text = '';
        this.value = [];
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
        this.element.trigger(":change");
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
        var element = this.element;
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
        element.append(value);
        element.append(pointer);
        element.append(show_wrapper);
        element.append(options);
        return [value, pointer, show_wrapper, options]
    }
}


class MultiLevelDropdown extends Dropdown {
    constructor(id, data, type, placeholder) {
        super(id, data, type, placeholder);
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
        this.element.trigger(':change');
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
    constructor(id, header, content, action_func) {
        super();
        this.element = $('#' + id);
        this.modal_element = this.element.find('.modal');
        this.header_text = header;
        this.content_text = content;
        this.action_func = action_func;
        this.offset_height = 30;
        this.build();
        this.listeners();
        this.show();
    }

    listeners() {
        this.element.find('.cancel.btn').click({object: this, func: this.hide}, this.dispatch);
        this.element.find('.action').click({object: this, func: this.hide}, this.dispatch);
        this.element.find('.action').click(this.action_func);
    }

    show() {
        this.element.addClass('visible');
        this.modal_element.addClass('show');
    }

    hide() {
        this.modal_element.removeClass('show');
        this.element.removeClass('visible');
    }

    build() {
        var header = this.element.find('.header');
        header.text(this.header_text);
        var content_container = this.element.find('.content-container');
        for (let i=0; i<this.content_text.length; i++) {
            var content_element = $('<p/>').addClass('content').text(this.content_text[i]);
            content_container.append(content_element);
        }
    }
}