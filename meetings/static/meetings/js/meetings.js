class CalendarMenu extends Menu {
    constructor(id, menu_btn_selector) {
        super(id, menu_btn_selector);
        this.site_select = new MenuSiteSelect('menu_site_select', 'checkbox');
    }
}



class AttendanceSelect extends JqueryElement {
    constructor(id, field_id, parent) {
        super(id, parent);
        this.default_value = [];
        this.value = this.default_value;
        this.data = [];
        this.val_to_text = {};
        this.form_field = $('#' + field_id);
        this.update_select();
    }

    update_select() {
        this.element.empty();
        this.form_field.empty();
        for (let i=0; i<this.data.length; i++) {
            this.build_member(this.data[i]);
            this.build_form_option(this.data[i]);
        }
        this.update_display();
        this.item_listeners();
    }

    select(option, e) {
        var input = $(option).find('input');
        if (!$(e.target).is('input') && !$(e.target).is('a')) {
            input.prop('checked', !input.prop('checked'));
        }
        var value = parseInt($(input).val());
        var text = $(input).siblings('a').text();
        if ($(input).is(':checked')) {
            this.value.push(value);
            this.val_to_text[value] = text;
        } else {
            this.value.splice(this.value.indexOf(value), 1);
            delete this.val_to_text[value];
        }
        this.update_display();
        this.element.trigger(':change');
    }

    update_display() {
        var select = this;
        this.val_to_text = {};
        this.element.find('input').each(function() {
            if (select.value.includes(parseInt($(this).val()))) {
                $(this).prop('checked', true);
                select.val_to_text[$(this).val()] = $(this).siblings('a').text();
            } else {
                $(this).prop('checked', false);
            }
        });
    }

    set_value(value) {
        this.value = value;
        this.update_display();
        this.element.trigger(':change');
    }

    build_member(member_data) {
        var item = $('<div/>')
            .addClass('attendance-item')
        item.append(
            $('<input/>')
                .attr('type', 'checkbox')
                .val(member_data[1])
        );
        item.append(
            $('<a/>')
                .text(member_data[0])
                .attr('href', url_profile_detail.slice(0,-2) + member_data[1])
                .attr('target', '_blank')
        );
        this.element.append(item);
        return item;
    }

    build_form_option(member_data) {
        var option = $('<option/>')
            .text(member_data[0])
            .val(member_data[1]);
        if (this.value.includes(member_data[1])) {
            option.prop('selected', true);
        }
        this.form_field.append(option);
    }

    item_listeners() {
        this.element.find('.attendance-item').click({func: this.select, object: this}, this.dispatch);
    }
}




class AttendanceSlide extends JqueryElement {
    constructor(id, parent) {
        super(id, parent);
        this.list_select = new Dropdown('list_select', [], {placeholder: 'Lists'});
        this.attendance_select = new AttendanceSelect('attendance_select', 'id_attendees', this);
        this.default_value = '{}'; // module_pk hash to profiles to add to or 'all'
        this.value = this.default_value; // module_pk hash to profiles to add to or 'all'
        this.messages = this.element.find('.messages');
        this.loader = this.element.find('.loading');
        this.close_selector = '#' + this.id + ', #meeting_info_container, .modal-container';
        this.listeners();
    }

    show() {
        this.element.addClass('show');
        closeFunctions[this.close_selector] = this;
    }

    hide() {
        this.element.removeClass('show');
        delete closeFunctions['#' + this.id + ', #attendance_btn'];
    }

    toggle() {
        if (this.element.hasClass('show')) {
            this.hide();
        } else {
            this.show();
        }
    }

    get_members(pk) {
        if (!pk) {
            return
        }
        var data = {
            'lists': JSON.stringify(this.list_select.value),
            'meeting': pk,
        }
        $.ajax({
            url: url_get_members,
            data: data,
            context: this,
            beforeSend: function() {
                this.loader.show();
            },
            success: function(data) {
                this.attendance_select.data = data['members'];
                this.attendance_select.update_select();
            },
            error: function () {
                addAlertHTML("Something went wrong.", 'danger');
            },
            complete: function() {
                this.loader.hide();
            }
        });
    }

    set_value(val) {
        this.value = val;
        this.element.trigger(':change');
    }

    modal_select(option, e) {
        // this is modal
        var modal = this
        var input = $(option).find('input');
        if (!$(e.target).is('input') && !$(e.target).is('a')) {
            input.prop('checked', !input.prop('checked'));
        }
        if (input.val() == 'all') {
            this.element.find('input').prop('checked', input.prop('checked'));
        }
        var all_checked = true;
        this.element.find('input').not('.all').each(function() {
            if (!$(this).prop('checked')) {
                all_checked = false;
            }
        });
        this.element.find('input.all').prop('checked', all_checked);
    }

    module_modal(elem) {
        var module_id = parseInt($(elem).attr('data-pk'));
        var title = $(elem).attr('data-title');
        var attendance_slide = this;
        var build_func = function() {
            var modal = this;
            var select = attendance_slide.attendance_select;
            this.id = module_id;
            var module_value = JSON.parse(attendance_slide.value)[module_id];

            this.element.find('.content-container').empty()
            this.element.find('.header-text').text('Attendees Receiving - ' + title + ' - Training');
            this.element.find('.action.btn').attr('class', 'btn action btn-primary');

            this.element = this.element.find('.content-container');
            this.element.addClass('attendance-select');
            var attendees = select.value;
            var all_option = select.build_member.call(this, ['All', 'all']).find('input');
            all_option.addClass('all');
            if (module_value == 'all') {
                all_option.prop('checked', true);
            }
            for (let i=0; i<attendees.length; i++) {
                var id = attendees[i];
                var item = select.build_member.call(this, [select.val_to_text[id], id]);
                if (module_value == 'all' || module_value.includes(id)) {
                    item.find('input').prop('checked', true);
                }
            }
            this.element.find('.attendance-item').click({object: this, func: attendance_slide.modal_select}, this.dispatch)

            this.element = this.element.closest('.modal');
            this.element.on(':hide', function() {
               setTimeout(function() {modal.element.find('.attendance-select').removeClass('attendance-select');}, 500);
            });
        }
        this.modal = new Modal('modal', {
            build_func: build_func,
            action_func: this.dispatch,
            action_data: {object: this, func: this.modal_submit}
        });
    }

    modal_submit() {
        var attendance_slide = this;
        var all_checked = attendance_slide.modal.element.find('input.all').prop('checked');
        var value = JSON.parse(attendance_slide.value);
        if (all_checked) {
            value[this.modal.id] = 'all';
        } else {
            value[this.modal.id] = [];
            attendance_slide.modal.element.find('input').not('.all').each(function() {
                if ($(this).prop('checked')) {
                    value[attendance_slide.modal.id].push(parseInt($(this).val()));
                }
            });
        }
        attendance_slide.value = JSON.stringify(value);
        attendance_slide.element.trigger(':change');
        attendance_slide.update_module_info();
    }

    update_module_info() {
        this.messages.empty();
        var modules = this.parent.training_select.value;
        var value = JSON.parse(this.value);
        // Add newly selected modules
        for (let i=0; i<modules.length; i++) {
            var id = modules[i];
            this.build_module_message(id);
            if (!value.hasOwnProperty(id)) {
                value[id] = [];
            }
        }
        // Get rid of unselected trainings
        for (const module_id in value) {
            if (!modules.includes(parseInt(module_id)) && !modules.includes(module_id.toString())) {
                delete value[module_id];
            }
        }
        var old_value = this.value;
        this.value = JSON.stringify(value);
        if (this.value != old_value) {
            this.element.trigger(':change');
        }
    }

    build_module_message(id) {
        var attendees = JSON.parse(this.value)[id];
        var title = this.parent.training_select.val_to_text[id];
        var container = $('<div/>');
        var modal_text = $('<a/>').attr('href', '#')
                         .attr('data-pk', id).attr('data-title', title);
        if (attendees == 'all') {
            modal_text.text('All');
        } else {
            modal_text.text('Selected');
        }
        var message = $('<p/>').text(' attendees will receive - ' + title + ' - training.');
        container.append(modal_text);
        container.append(message);
        this.messages.append(container);
        this.item_listeners();
    }

    item_listeners() {
        this.messages.find('a').click({func: this.module_modal, object: this}, this.dispatch);
    }

    listeners() {
        this.element.find('.back').click({func: this.hide, object: this}, this.dispatch);
        this.parent.training_select.element.on(':change', {func: this.update_module_info, object: this}, this.dispatch);
        this.parent.training_select.element.on(':update', {func: this.update_module_info, object: this}, this.dispatch);
    }
}



class StartTime extends JqueryElement {
    constructor(id, date_select, time_select) {
        super(id);
        this.date_select = date_select;
        this.time_select = time_select;
        this.default_value = "0000-00-00T12:00:00Z"
        this.listeners();
    }

    update_value() {
        this.value = getDatetime(this.date_select, this.time_select)[0];
        this.element.trigger(":change");
    }

    set_value(value) {
        this.value = value
        this.listeners_off();
        this.date_select.set_value([value.slice(0, 10)]);
        this.time_select.set_value(value.slice(11, 19), true, false);
        this.listeners();
        this.update_value();
    }

    listeners_off() {
        this.date_select.element.off(":change.starttime");
        this.time_select.element.off(":change.starttime");
    }

    listeners() {
        this.listeners_off();
        this.date_select.element.on(":change.starttime", {func: this.update_value, object: this}, this.dispatch)
        this.time_select.element.on(":change.starttime", {func: this.update_value, object: this}, this.dispatch)
    }
}




class EndTime extends StartTime {

    update_value() {
        this.value = getDatetime(this.date_select, this.time_select)[1];
        this.element.trigger(":change");
    }

    listeners_off() {
        this.date_select.element.off(":change.endtime");
        this.time_select.element.off(":change.endtime");
    }

    listeners() {
        this.listeners_off();
        this.date_select.element.on(":change.endtime", {func: this.update_value, object: this}, this.dispatch)
        this.time_select.element.on(":change.endtime", {func: this.update_value, object: this}, this.dispatch)
    }
}




class TypeSelect extends JqueryElement {
    constructor(id) {
        super(id);
        this.value = '';
        this.input = this.element.find('input');
        this.close_selector = '#' + this.id + ' .options';
        this.listeners();
    }

    set_value(value) {
        this.value = value;
        this.input.val(value);
        expandTitle('Type');
    }

    show() {
        this.element.find('.options').addClass('visible');
        this.element.find('.options-wrapper').addClass('show');
        closeFunctions[this.close_selector] = this
    }

    hide() {
        this.element.find('.options').removeClass('visible');
        this.element.find('.options-wrapper').removeClass('show');
        delete closeFunctions[this.close_selector];
    }

    toggle() {
        if (this.element.find('.options-wrapper').hasClass('show')) {
            this.hide();
        } else {
            this.show();
        }
    }

    select(type) {
        var value = $(type).find('p').text();
        this.value = value;
        if (value == "Custom Type") {
            this.input.attr('readonly', false);
            this.input.val('');
            this.value = '';
            this.input.focus();
        } else {
            this.input.val(value);
        }
        expandTitle('Type');
    }

    update_value() {
        this.value = this.input.val();
        this.element.trigger(':change');
    }

    unfocus() {
        this.input.attr("readonly", "readonly");
    }

    listeners() {
        this.element.click({func: this.toggle, object: this}, this.dispatch);
        this.element.find('.type').click({func: this.select, object: this}, this.dispatch);
        this.input.on("blur", {func: this.unfocus, object: this}, this.dispatch);
        this.input.change({func: this.update_value, object: this}, this.dispatch);
    }
}




class ProgrammingSelect extends ObjectSelect {

    get_object_url(object_info) {
        var url = this.object_url;
        url += '?site=' + this.parent.site_select.value[0];
        url += '&type=Programming'
        url += '&model_type=programming'
        url += '&id=' + object_info[1];
        return url
    }

}




class ModuleSelect extends MultiLevelObjectSelect {

    get_object_url(object_info) {
        var url = this.object_url;
        url += '?site=' + this.parent.site_select.value[0];
        url += '&type=All'
        url += '&model_type=module'
        url += '&id=' + object_info[1];
        return url
    }

}




class MeetingInfo extends JqueryElement {
    constructor(id, parent) {
        super(id, parent);
        this.pk = 0;
        this.changes_saved = true;
        this.site_select = new Dropdown('meeting_site_select', [], {type: 'radio'});
        this.type_select = new TypeSelect('type_select');
        this.color_select = new ColorPicker('meeting_color');
        this.date_select = new MultiDatePicker('meeting_date');
        this.time_select = new TimePicker('meeting_time');
        this.start_time = new StartTime('id_start_time', this.date_select, this.time_select);
        this.end_time = new EndTime('id_end_time', this.date_select, this.time_select);
        this.programming_select = new ProgrammingSelect('programming_select', [], 'id_programming', {object_url: url_learning + 'programming', parent: this});
        this.training_select = new ModuleSelect('training_select', [], 'id_modules', {object_url: url_learning + 'module', parent: this});
        this.attendance = new AttendanceSlide('attendance_container', this);
        this.file_input = new FileInput('file_input');
        form_fields['files'] = 'json'
        this.link_input = new LinkInput('link_input');
        var custom_fields = {
            'color': this.color_select,
            'site': this.site_select,
            'type': this.type_select,
            'start_time': this.start_time,
            'end_time': this.end_time,
            'programming': this.programming_select,
            'modules': this.training_select,
            'modules_to_attendees': this.attendance,
            'links': this.link_input,
            'files': this.file_input,
            'lists': this.attendance.list_select,
            'attendees': this.attendance.attendance_select,
        }
        this.form = new CustomForm('meeting_form', custom_fields, form_fields, 'id_')
        this.get_user_lists();
        this.loader = this.element.find('.loading');
        this.listeners();
    }

    show(pk, date) {
        this.pk = null; // reset pk
        this.form.erase_data();

        // Set site select options
        var sites = this.get_site_select_data();
        this.site_select.data = sites;
        this.site_select.initialize();

        // Sync month in date picker with calendar month
        this.element.trigger(":monthsync");
        if (pk) {
            this.pk = pk;
            this.get_meeting_info();
        } else {
            this.pk = 0;
            var first_site_value = this.site_select.element.find('.option').first().find('input').val();
            this.site_select.set_value(first_site_value);
            this.date_select.set_value([date]);
        }


        this.element.addClass('show');
        this.attendance.element.addClass('modal-shadow');
    }

    hide(element, e, data) {
        var force = (data && data.hasOwnProperty('force')) ? data.force : false;
        if (!this.changes_saved && !force) {
            this.discard_changes_modal();
            return
        }
        this.attendance.hide();
        this.element.removeClass('show');
        this.attendance.element.removeClass('modal-shadow');
    }

    discard_changes_modal() {
        var type = this.type_select.value;
        type = type ? type : 'Meeting';
        var site = this.site_select.element.find('input:checked').siblings('p').text();
        var build_func = function() {
            this.element.find('.header-text').text('Discard Changes?');
            this.element.find('.action.btn').attr('class', 'btn action btn-danger');
            var text = $('<p/>').text([site, type].join(' - ')).addClass('text-medium');
            var content = this.element.find('.content-container');
            content.empty();
            content.append(text);
        }
        var action_data = {func: this.hide, object: this, extra_data: {'force': true}};
        new Modal('modal', {
            build_func: build_func,
            action_func: this.dispatch,
            action_data: action_data,
        });
    }

    get_meeting_info() {
        var data = {
            'pk': this.pk,
            'lists': [],
        }
        $.ajax({
            url: url_get_meeting_info,
            type: 'GET',
            data: data,
            context: this,
            beforeSend: function() {
                this.loader.show();
            },
            success: this.initialize_form,
            complete: function() {
                this.loader.hide();
            },
        });
    }

    initialize_form(data) {
        this.form.set_data(data.meeting_data);
        this.changes_saved = true;
    }

    submit_form() {
        if (!this.form_validation()) {
            return
        }
        var data = this.file_input.form_data;
        data.append('form', this.form.element.serialize());
        data.append('dates', JSON.stringify(this.date_select.value));
        data.append('delete_files', JSON.stringify(this.file_input.delete_files));
        var csrftoken = $('[name = "csrfmiddlewaretoken"]').val();
        $.ajax({
            url: url_meeting_post.slice(0,-1) + this.pk,
            type: 'post',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            data: data,
            processData: false,
            contentType: false,
            context: this,
            beforeSend: function() {
                this.loader.show();
                this.attendance.loader.show();
            },
            success: this.submit_success,
            complete: function () {
                this.loader.hide();
                this.attendance.loader.hide();
            },
            error: function() {
            },
        });
    }

    form_validation() {
        if (!this.date_select.value || this.date_select.value.length < 1) {
            addAlertHTML('At least one date required.', 'danger');
            return false
        }
        if (!this.type_select.value || this.type_select.value.length < 1) {
            addAlertHTML('Meeting type required.', 'danger');
            return false
        }
        return true
    }

    submit_success(data) {
        this.pk = data.id;
        this.form.set_data(data);
        this.changes_saved = true;
        this.element.trigger(":reload");
    }

    delete_meeting_modal() {
        if (!this.changes_saved) {
            addAlertHTML('Save changes before deleting.', 'secondary');
            return
        }
        var type = this.type_select.value;
        var site = this.site_select.element.find('input:checked').siblings('p').text();
        var build_func = function() {
            this.element.find('.action.btn').attr('class', 'btn action btn-danger');
            this.element.find('.header-text').text('Delete Meeting?');
            var text = $('<p/>').text([site, type].join(' - ')).addClass('text-medium');
            var content = this.element.find('.content-container');
            content.empty();
            content.append(text);
        }
        var action_data = {func: this.delete_meeting, object: this};
        new Modal('modal', {
            build_func: build_func,
            action_func: this.dispatch,
            action_data: action_data,
        });
    }

    delete_meeting() {
        var csrftoken = $('[name = "csrfmiddlewaretoken"]').val();
        $.ajax({
            url: url_delete_meeting.slice(0,-1) + this.pk,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            context: this,
            beforeSend: function() {
                this.loader.show();
            },
            success: function() {
                this.hide();
                this.element.trigger(':reload');
            },
            error: function() {
                addAlertHTML('Something went wrong.', 'danger');
            },
            complete: function() {
                this.loader.hide();
            },
        });
    }

    get_learning_data() {
        // Site not yet set
        if (!this.site_select.value[0]) {
            return
        }
        var data = {
            'site': this.site_select.value[0],
            'get_site_models': true,
        };
        $.ajax({
            url: url_learning_models,
            data: data,
            context: this,
            beforeSend: function() {
                this.loader.show();
            },
            success: this.learning_data_success,
            error: function() {
                addAlertHTML('Something went wrong.', 'danger');
            },
            complete: function() {
                this.loader.hide();
            },
        });
    }

    learning_data_success(data) {
        data = data.site_data;
        var programming_options = [];
        for (let i=0; i<data.programming.length; i++) {
            programming_options.push(data.programming[i][1]);
        }
        this.remove_missing_values(this.programming_select, programming_options);
        this.programming_select.data = data.programming;
        this.programming_select.update_select();
        var theme_data = [];
        var module_options = [];
        for (let i=0; i<data.themes.length; i++) {
            var theme = data.themes[i];
            var modules = theme.modules;
            var module_data = [];
            for (let j=0; j<modules.length; j++) {
                module_data.push(modules[j].slice(0,2));
                module_options.push(modules[j][1]);
            }
            theme = theme.theme.slice(0,2);
            theme.push(module_data);
            theme_data.push(theme)
        }
        this.remove_missing_values(this.training_select, module_options);
        this.training_select.data = theme_data;
        this.training_select.update_select();
    }

    remove_missing_values(object, values) {
        var new_value = [];
        for (let i=0; i<object.value.length; i++) {
            if (values.includes(object.value[i])) {
                new_value.push(object.value[i]);
            }
        }
        object.value = new_value;
    }

    get_user_lists() {
        var list_select = this.attendance.list_select
        list_select.data = [];
        $('#id_lists').find('option').each(function() {
            list_select.data.push([$(this).text(), $(this).val()]);
        });
        list_select.initialize();
    }

    get_site_select_data() {
        var sites = [];
        $('#menu .menu-site-select').find('.site').each(function() {
            if ($(this).find('input').is(':checked')) {
                var site_text = $(this).find('.site-text').text();
                var site_pk = $(this).find('input').val();
                sites.push([site_text, site_pk]);
            }
        });
        return sites
    }

    listeners() {
        var meeting_info = this
        this.element.find('.back').click({func: this.hide, object: this}, this.dispatch);
        this.element.find('.back').click({func: this.parent.update_url, object: this.parent}, this.dispatch);
        this.element.find('#attendance_btn').click({func: this.attendance.toggle, object: this.attendance}, this.dispatch);
        this.element.find('#meeting_submit_btn').click({func: this.submit_form, object: this}, this.dispatch);
        this.element.find('#meeting_delete_btn').click({func: this.delete_meeting_modal, object: this}, this.dispatch);
        this.form.element.on(':change', function() {meeting_info.changes_saved = false});
        this.attendance.list_select.element.on(':change', function() {meeting_info.attendance.get_members(meeting_info.pk)});
        this.site_select.element.on(':change', {func: this.get_learning_data, object: this}, this.dispatch);
    }
}




class Calendar extends JqueryElement {
    constructor(id) {
        super(id);
        this.month_offset = 0;
        this.meetings = {};
        this.meetings_request = null;
        this.month = this.element.find('.month');
        this.year = this.element.find('.year');
        this.days = this.element.find('.days-container');
        this.loader = this.element.find('.loading');
        this.menu = new CalendarMenu('menu', 'menu_btn');
        this.meeting_info = new MeetingInfo('meeting_info_container', this);
        this.site_select = this.menu.site_select;
        this.site_select.select(this.site_select.element.find('.all'));
        this.reload_month();
        this.listeners();
    }

    reload_month() {
        this.show_month(this.month_offset, 0);
    }

    show_month(month_offset, step) {
        var dates = getMonthDates(month_offset + step);
        this.view = dates[2];
        this.month.text(this.view.format('MMMM'));
        this.month.attr('data-number', this.view.format('MM'));
        this.year.text(this.view.format('YYYY'));
        var current_date = dates[1];
        this.dates = dates[0];

        // True means meetings were queried and rest was handled by success
        if (!this.check_meetings_query(month_offset, step, current_date[0], current_date[1])) {
            this.show_weeks();
        }
    }

    change_month(btn) {
        if ($(btn).hasClass('next')) {
            this.show_month(this.month_offset++, 1)
        } else if ($(btn).hasClass('previous')) {
            this.show_month(this.month_offset--, -1)
        }
    }

    show_weeks() {
        this.days.empty();
        var i = 0;
        for (i; i<(this.dates.length/7); i++) {
            var j = 0;
            var days = []
            for (j; j<7; j++) {
                var view_moment = this.view.clone();
                var monthnum = this.dates[(i*7) + j];
                // Check for meetings on this day
                if (i == 0 && monthnum > 7) {
                    day = view_moment.add(-1, 'month').format('-MM-YYYY');
                } else if (i > 3 && monthnum < 7) {
                    day = view_moment.add(1, 'month').format('-MM-YYYY');
                } else {
                    day = view_moment.format('-MM-YYYY');
                }
                day = monthnum.toString().padStart(2, '0') + day;
                var found_meetings = this.meetings[day];
                if (!found_meetings) {
                    found_meetings = [];
                }
                var active = true;
                if ((i==0 && monthnum>7) || (i==this.dates.length/7-1 && monthnum<7)) {
                    active = false;
                }
                var day = {monthnum: monthnum, meetings: found_meetings, active: active};
                days.push(day);
            }
            var include_site = (this.site_select.value.length > 1) ? true : false;
            this.build_week(days, include_site);
        }
        this.item_listeners();
    }

    check_meetings_query(month_offset, step, current_year, current_month) {
        var meetings_basemonthoffset = floorbase32(month_offset + step + 16) - 16;
        if (floorbase32(month_offset + 16) - 16 != meetings_basemonthoffset || !step) {
            var current_date = moment().year(current_year).month(current_month-1);
            var base_date = current_date.add(meetings_basemonthoffset - 1, 'month');
            var baseyear = base_date.format('YYYY');
            var basemonth = base_date.format('MM');
            var end_date = base_date.add(32 + 2, 'month');
            var endyear = end_date.format('YYYY');
            var endmonth = end_date.format('MM');
            this.get_meetings(baseyear, basemonth, endyear, endmonth);
            return true
        }
        return false
    }

    get_meetings(baseyear, basemonth, endyear, endmonth) {
        if (this.meetings_request) {
            this.aborted = true;
            this.meetings_request.abort();
        }
        var sites = JSON.stringify(this.site_select.value);
        var data = {
            'site_pks': sites,
            'baseyear': baseyear,
            'basemonth': basemonth,
            'endyear': endyear,
            'endmonth': endmonth,
        }
        this.meetings_request = $.ajax({
            url: "get-meetings",
            data: data,
            method: 'GET',
            context: this,
            beforeSend: function() {
                this.loader.show();
            },
            complete: function() {
                this.loader.hide();
            },
            success: this.get_meetings_success,
            error: function() {
                if (this.aborted) {
                    this.aborted = false;
                    return
                }
                addAlertHTML('Something went wrong.', 'danger');
            }
        });
    }

    get_meetings_success(data) {
        this.meetings_request = null;
        this.meetings = {};
        for (var i=0; i<data.meetings.length; i++) {
            var meeting = data.meetings[i];
            var obj = moment.parseZone(meeting['start_time']);
            var date = obj.format('DD-MM-YYYY');
            var time = obj.format('HH-mm');
            try {
                this.meetings[date].push(meeting);
            } catch(err) {
                this.meetings[date] = [meeting];
            }
        }
        this.show_weeks();
    }

    make_meeting_text_color(color_str) {
        var s = (parseInt(color_str.slice(10,12),10) + 20).toString();
        var l = (parseInt(color_str.slice(15,17),10) - 35).toString();
        var a = 1.0.toString();
        var hsla = color_str.slice(0,10) + s + '%, ' + l + '%, ' + a + ')';
        return hsla;
    }

    month_sync() {
        this.meeting_info.date_select.month_offset = this.month_offset;
    }

    update_url(change) {
        var sites = this.site_select.value
        var url = '?';
        for (let i=0; i<sites.length; i++) {
            url += i ? '&' : '';
            url += 'sites[]=' + sites[i].toString();
        }
        if (!sites.length) {
            url += '&sites[]=';
        }
        if ($(change).hasClass('calendar-meeting')) {
            url += '&meeting=' + $(change).attr('data-pk');
        }
        if ($(change).hasClass('add-meeting-btn')) {
            var year = this.year.text();
            var month = this.month.attr('data-number');
            var day = $(change).siblings('.monthnum').text().padStart(2, '0');
            var date = [year, month, day].join('-');
            url += '&new_meeting=' + date;
        }
        history.pushState({}, '', url);
        $(window).trigger('popstate');
    }

    build_week(days, include_site) {
        ///// Calendar Week HTML ////////
        var week = $('<ul/>')
            .addClass('calendar-week');
        for (var i=0; i<days.length; i++) {
            /////// Day Box HTML /////////
            var day = $('<li/>')
                .addClass('calendar-day');
            if (!days[i]['active']) {
                day.addClass('inactive');
            } else {
            ////// Add Meeting Button ////
                var add_btn = $('<i/>')
                    .addClass('add-meeting-btn fas fa-plus blacklink')
                day.append(add_btn);
            }
            ///// Month Number HTML //////
            var day_monthnum = $('<p/>')
                .text(days[i]['monthnum'])
                .addClass('monthnum')
            day.append(day_monthnum);
            /////// Meetings HTML //////
            var meetings_container = $('<div/>')
                .addClass('meetings-container');
            for (var j=0; j<days[i]['meetings'].length; j++) {
                var meeting_info = days[i]['meetings'][j];
                var color = meeting_info['color'];
                var text_color = this.make_meeting_text_color(color);
                var meeting = $('<div/>')
                    .addClass('calendar-meeting relative')
                    .css('background-color', color)
                    .attr('data-pk', meeting_info['pk'])
                    .attr('data-sitepk', meeting_info['site']);
                var title = $('<p/>')
                    .css('color', text_color)
                    .addClass('meeting-description');
                if (include_site) {
                    title.text(meeting_info['site'] + ' - ' + meeting_info['type'])
                } else {
                    title.text(meeting_info['type']);
                }
                var click_wrapper = $('<span/>')
                    .addClass('show-wrapper');
                meeting.append(click_wrapper);
                meeting.append(title)
                meetings_container.append(meeting);
            }
            day.append(meetings_container);
            var spacer = $('<div/>')
                .addClass('spacer')
                .text('spacer');
            day.append(spacer);
            week.append(day);
        }
        this.days.append(week);
    }

    item_listeners() {
        this.element.find('.add-meeting-btn').click({func: this.update_url, object: this}, this.dispatch);
        this.element.find('.calendar-meeting').click({func: this.update_url, object: this}, this.dispatch);
    }

    listeners() {
        this.element.find('.next').click({func: this.change_month, object: this}, this.dispatch);
        this.element.find('.previous').click({func: this.change_month, object: this}, this.dispatch);
        this.site_select.element.on(":change", {func: this.update_url, object: this}, this.dispatch);
        this.site_select.element.on(":change", {func: this.reload_month, object: this}, this.dispatch);
        this.meeting_info.element.on(":reload", {func: this.reload_month, object: this}, this.dispatch);
        this.meeting_info.element.on(":monthsync", {func: this.month_sync, object: this}, this.dispatch);
    }
}




function floorbase32(int) {
    return Math.floor(int / 32) * 32;
}


// date_select value: ['yy-mm-dd', ]
// time_select value: ['hh:mm:00']
// returns [start_datetime, end_datetime]
function getDatetime(date_select, time_select) {
    var datetimes = [];
    for (let i=0; i<time_select.value.length; i++) {
        var date = date_select.value[0]; // first date
        var time = time_select.value[i]; // 0 = start. 1 = end.
        datetime = date + ' ' + time;
        datetimes.push(datetime);
    }
    return datetimes
}




function update_page() {
    var query = parseQuery(window.location.search);
    if (query.sites) {
        query.sites = (query.sites[0] == '') ? [] : query.sites; // None selected
        var old = calendar.site_select.value;
        if (!arraysEqual(old, query.sites)) {
            calendar.site_select.set_value(query.sites, true);
        }
    }
    if (query.meeting) {
        calendar.meeting_info.show(query.meeting);
    }
    if (query.new_meeting) {
        calendar.meeting_info.show(0, query.new_meeting);
    }
    if (query.programming) {
        calendar.meeting_info.programming_select.set_value([parseInt(query.programming)]);
    }
    if (query.module) {
        calendar.meeting_info.training_select.set_value([parseInt(query.module)]);
    }
}

var calendar;
$(document).ready(function() {
    calendar = new Calendar('calendar');
    $(window).on('popstate', update_page);
    $(window).trigger('popstate');
});