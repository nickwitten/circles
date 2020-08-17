class CalendarMenu extends Menu {
    constructor(id, menu_btn_selector) {
        super(id, menu_btn_selector);
        this.site_select = new MenuSiteSelect('menu_site_select', 'checkbox');
    }
}




class Attendance extends JqueryElement {
    constructor(id) {
        super(id);
        this.list_select = new Dropdown('list_select', [], {placeholder: 'Lists'});
        this.listeners();
        this.close_selector = '#' + this.id + ', #attendance_btn';
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

    set_value() {
    }

    listeners() {
        this.element.find('.back').click({func: this.hide, object: this}, this.dispatch);
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
        this.date_select.set_value([value.slice(0, 10)]);
        this.time_select.set_value(value.slice(11, 19), true, false);
    }

    listeners() {
        this.date_select.element.on(":change", {func: this.update_value, object: this}, this.dispatch)
        this.time_select.element.on(":change", {func: this.update_value, object: this}, this.dispatch)
    }
}




class EndTime extends JqueryElement {
    constructor(id, date_select, time_select) {
        super(id);
        this.date_select = date_select
        this.time_select = time_select;
        this.default_value = "0000-00-00T12:00:00Z"
        this.listeners();
    }

    update_value() {
        this.value = getDatetime(this.date_select, this.time_select)[1];
        this.element.trigger(":change");
    }

    set_value(value) {
        this.value = value;
        this.date_select.set_value([value.slice(0, 10)]);
        this.time_select.set_value(value.slice(11, 19), false, true);
    }

    listeners() {
        this.date_select.element.on(":change", {func: this.update_value, object: this}, this.dispatch)
        this.time_select.element.on(":change", {func: this.update_value, object: this}, this.dispatch)
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
        var value = $(type).find('a').text();
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




class MeetingInfo extends JqueryElement {
    constructor(id) {
        super(id);
        this.pk = 0;
        this.changes_saved = true;
        this.site_select = new Dropdown('meeting_site_select', [], {type: 'radio'});
        this.attendance = new Attendance('attendance_container')
        this.type_select = new TypeSelect('type_select');
        this.color_select = new ColorPicker('meeting_color');
        this.date_select = new MultiDatePicker('meeting_date');
        this.time_select = new TimePicker('meeting_time');
        this.start_time = new StartTime('id_start_time', this.date_select, this.time_select);
        this.end_time = new EndTime('id_end_time', this.date_select, this.time_select);
        this.programming_select = new ObjectSelect('programming_select', []);
        this.training_select = new ObjectSelect('training_select', []);
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
            'links': this.link_input,
            'files': this.file_input,
        }
        this.form = new CustomForm('meeting_form', custom_fields, form_fields, 'id_')
        this.type_select.element.trigger(":change"); // Only for test. REMOVE
        this.color_select.element.trigger(":change");
        this.link_input.element.trigger(":change");
        this.loader = this.element.find('.loading');
        this.listeners();
    }

    show(pk, date) {
        this.form.erase_data();
        if (pk) {
            this.pk = pk;
            this.get_meeting_info();
        } else {
            this.pk = 0;
        }

        // Set site select options
        var sites = this.get_site_select_data();
        this.site_select.data = sites;
        this.site_select.initialize();
        var first_site_value = this.site_select.element.find('.option').first().find('input').val();
        this.site_select.set_value(first_site_value);

        // Set date
        if (date) {
            this.date_select.set_value([date]);
        }
        this.element.trigger(":monthsync");

        this.element.addClass('show');
        this.attendance.element.addClass('modal-shadow');
        this.get_user_filtersets();
    }

    hide(element, e, data) {
        var force = (data && data.hasOwnProperty('force')) ? data.force : false;
        if (!this.changes_saved && !force) {
            this.discard_changes_modal();
            return
        }
        this.element.removeClass('show');
        this.attendance.element.removeClass('modal-shadow');
    }

    discard_changes_modal() {
        var type = this.type_select.value;
        var site = this.site_select.element.find('input:checked').siblings('p').text();
        var build_func = function() {
            this.element.find('.header-text').text('Discard Changes?');
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
            },
            success: this.submit_success,
            complete: function () {
                this.loader.hide();
            },
            error: function() {
            },
        });
    }

    form_validation() {
        if (this.date_select.value.length < 1) {
            addAlertHTML('At least one date required.', 'danger');
            return false
        }
        if (this.type_select.value.length < 1) {
            addAlertHTML('Meeting type required.', 'danger');
            return false
        }
        return true
    }

    submit_success(data) {
        this.pk = data.id;
        this.form.set_data(data);
        this.changes_saved = true;
        this.element.trigger(":update");
    }

    delete_meeting_modal() {
        console.log(this.changes_saved);
        if (!this.changes_saved) {
            addAlertHTML('Save changes before deleting.', 'secondary');
            return
        }
        var type = this.type_select.value;
        var site = this.site_select.element.find('input:checked').siblings('p').text();
        var build_func = function() {
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
                this.element.trigger(':update');
            },
            error: function() {
                addAlertHTML('Something went wrong.', 'danger');
            },
            complete: function() {
                this.loader.hide();
            },
        });
    }

    get_user_filtersets() {

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
        this.element.find('#attendance_btn').click({func: this.attendance.toggle, object: this.attendance}, this.dispatch);
        this.element.find('#meeting_submit_btn').click({func: this.submit_form, object: this}, this.dispatch);
        this.element.find('#meeting_delete_btn').click({func: this.delete_meeting_modal, object: this}, this.dispatch);
        this.form.element.on(':change', function() {meeting_info.changes_saved = false});
    }
}




class Calendar extends JqueryElement {
    constructor(id) {
        super(id);
        this.monthOffset = 0;
        this.meetings = {};
        this.month = this.element.find('.month');
        this.year = this.element.find('.year');
        this.days = this.element.find('.days-container');
        this.loader = this.element.find('.loading');
        this.menu = new CalendarMenu('menu', 'menu_btn');
        this.meeting_info = new MeetingInfo('meeting_info_container');
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
            this.show_month(this.monthOffset++, 1)
        } else if ($(btn).hasClass('previous')) {
            this.show_month(this.monthOffset--, -1)
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
            var include_site = (this.site_select.site_ct > 1) ? true : false;
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
        var sites = JSON.stringify(this.site_select.value);
        var data = {
            'site_pks': sites,
            'baseyear': baseyear,
            'basemonth': basemonth,
            'endyear': endyear,
            'endmonth': endmonth,
        }
        $.ajax({
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
                addAlertHTML('Something went wrong.', 'danger');
            }
        });
    }

    get_meetings_success(data) {
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

    show_meeting(element) {
        var pk = null;
        var date = null;
        if ($(element).hasClass('calendar-meeting')) {
            var pk = $(element).attr('data-pk');
        } else {
            var year = this.year.text();
            var month = this.month.attr('data-number');
            var day = $(element).siblings('.monthnum').text().padStart(2, '0');
            date = [year, month, day].join('-');
        }
        this.meeting_info.show(pk, date);
    }

    make_meeting_text_color(color_str) {
        var s = (parseInt(color_str.slice(10,12),10) + 20).toString();
        var l = (parseInt(color_str.slice(15,17),10) - 35).toString();
        var a = 1.0.toString();
        var hsla = color_str.slice(0,10) + s + '%, ' + l + '%, ' + a + ')';
        return hsla;
    }

    month_sync() {
        this.meeting_info.date_select.month_offset = this.monthOffset;
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
                    .addClass('add-meeting-btn fas fa-plus')
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
                var click_wrapper = $('<a/>')
                    .attr('href', '#')
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
        this.element.find('.add-meeting-btn').click({func: this.show_meeting, object: this}, this.dispatch);
        this.element.find('.calendar-meeting').click({func: this.show_meeting, object: this}, this.dispatch);
    }

    listeners() {
        this.element.find('.next').click({func: this.change_month, object: this}, this.dispatch);
        this.element.find('.previous').click({func: this.change_month, object: this}, this.dispatch);
        this.site_select.element.on(":change", {func: this.reload_month, object: this}, this.dispatch);
        this.meeting_info.element.on(":update", {func: this.reload_month, object: this}, this.dispatch);
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


$(document).ready(function() {
    new Calendar('calendar');
});