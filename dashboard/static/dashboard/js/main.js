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


class Dropdown {
    constructor(id, data) {
        this.id = id;
        this.data = data;
        this.build();
        this.styles();
        $('#' + id + ' .show-wrapper').on('click',{select: this}, this.show);
    }

    show(event) {
        var dropdown = $('#' + event.data.select.id);
        dropdown.find('.options').addClass('visible');
        dropdown.find('.pointer').addClass('rotate');
        var options_wrapper = dropdown.find('.options-wrapper');
        options_wrapper.addClass('show');
        options_wrapper.css('top', '0');
        dropdown.find('.show-wrapper').hide();
        // Start checking for clicks outside
        closeFunctions['#' + event.data.select.id + ' .option'] = event.data.select;
    }

    hide() {
        var dropdown = $('#' + this.id);
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
        var dropdown = $('#' + this.id);
        var options_wrapper = dropdown.find('.options-wrapper');
        options_wrapper.css('top', '-' + options_wrapper.css('height'));
        var options = dropdown.find('.options');
        options.css('height', 'fit-content');
        options.height(options.height() + 10);
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
                .attr('type', 'checkbox')
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
    }
}


class MultiLevelDropdown {
    constructor(id, data, type) {
        this.id = id;
        this.data = data;
        this.type = type;
        this.build();
        this.styles();
        $('#' + id + ' .show-wrapper').on('click',{select: this}, this.show);
    }

    show(event) {
        var dropdown = $('#' + event.data.select.id);
        dropdown.find('.options').addClass('visible');
        dropdown.find('.pointer').addClass('rotate');
        var options_wrapper = dropdown.find('.options-wrapper');
        options_wrapper.addClass('show');
        options_wrapper.css('top', '0');
        dropdown.find('.show-wrapper').hide();
        // Start checking for clicks outside
        closeFunctions['#' + event.data.select.id + ' .option'] = event.data.select;
    }

    hide() {
        var dropdown = $('#' + this.id);
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
        var max_sub_height = 0;
        var select = this;
        $('#' + this.id).find('.option').each(function() {
            var height = select.hide_sub_wrapper.call(this);
            max_sub_height = (height>max_sub_height) ? height : max_sub_height;
            $(this).hover(select.show_sub_wrapper, select.hide_sub_wrapper);
        });
        var dropdown = $('#' + this.id);
        var options = dropdown.find('.options');
        options.css('height', 'fit-content');
        var new_height = max_sub_height + options.height();
        options.height(new_height);
        dropdown.find('.options-wrapper').each(function() {
            $(this).css('top', '-' + $(this).css('height'));
        });
        $(window).resize(this.styles);
    }

    show_sub_wrapper() {
        $(this).find('.sub-options-wrapper').css('top', '0');
    }

    hide_sub_wrapper() {
        var sub_wrapper = $(this).find('.sub-options-wrapper');
        var height = sub_wrapper.css("height");
        sub_wrapper.css('top', '-' + height);
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
            option.append(input);
            option.append(option_text);
            option.append(sub_options)
            options_wrapper.append(option)
        }
        options.append(options_wrapper);
        element.append(value);
        element.append(pointer);
        element.append(show_wrapper);
        element.append(options);
    }
}
