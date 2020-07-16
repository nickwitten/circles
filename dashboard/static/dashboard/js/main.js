var closeFunctions = {
}


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
        event.data.func.call(event.data.object, event_this);
    }
}

class Dropdown extends JqueryElement {
    constructor(id, data, type) {
        super();
        this.id = id;
        this.element = $('#' + this.id);
        this.data = data;
        this.type = type;
        this.build();
        this.styles();
        this.listeners();
    }

    listeners() {
        var dropdown = this;
        this.element.find('.show-wrapper').click({func: this.show, object: this}, this.dispatch);
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
                .attr('data-value', option_data[1]);
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
    constructor(id, data, type) {
        super(id, data, type);
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
                .attr('data-value', option_data[1]);
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