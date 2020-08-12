class CalendarMenu extends Menu {
    constructor(id, menu_btn_selector) {
        super(id, menu_btn_selector);
        this.site_select = new MenuSiteSelect('menu_site_select', 'checkbox');
    }
}




class Attendance extends JqueryElement {
    constructor(id) {
        super(id);
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

    listeners() {
        this.element.find('.back').click({func: this.hide, object: this}, this.dispatch);
    }
}



class StartTime extends JqueryElement {
    constructor(id, date_select, time_select) {
        super(id);
        this.date_select = date_select;
        this.time_select = time_select;
        this.listeners();
    }

    update_value() {
        this.value = getDatetime(this.date_select, this.time_select)[0];
        this.element.trigger(":change");
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
        this.listeners();
    }

    update_value() {
        this.value = getDatetime(this.date_select, this.time_select)[1];
        this.element.trigger(":change");
    }

    listeners() {
        this.date_select.element.on(":change", {func: this.update_value, object: this}, this.dispatch)
        this.time_select.element.on(":change", {func: this.update_value, object: this}, this.dispatch)
    }
}




class TypeSelect extends JqueryElement {
    constructor(id) {
        super(id);
        this.value = 'test';
    }
}




class MeetingInfo extends JqueryElement {
    constructor(id) {
        super(id);
        this.pk = null;
        this.site_select = new Dropdown('meeting_site_select', [], {type: 'radio'});
        this.attendance = new Attendance('attendance_container')
        this.type_select = new TypeSelect('meeting_title_container');
        this.color_select = new ColorPicker('color_select');
        this.date_select = new MultiDatePicker('meeting_date');
        this.time_select = new TimePicker('meeting_time');
        this.start_time = new StartTime('id_start_time', this.date_select, this.time_select);
        this.end_time = new EndTime('id_end_time', this.date_select, this.time_select);
        this.programming_select = new ObjectSelect('programming_select', []);
        this.training_select = new ObjectSelect('training_select', []);
        this.file_input = new FileInput('file_input');
        this.link_input = new LinkInput('link_input');
        var custom_fields = {
            'color': this.color_select,
            'site': this.site_select,
            'type': this.type_select,
            'start_time': this.start_time,
            'end_time': this.end_time,
            'links': this.link_input,
         }
        this.form = new CustomForm('meeting_form', custom_fields, form_fields, 'id_')
        this.type_select.element.trigger(":change"); // Only for test. REMOVE
        this.color_select.element.trigger(":change");
        this.link_input.element.trigger(":change");
        this.loader = this.element.find('.loading');
        this.listeners();
    }

    show(pk) {
        if (pk) {
            this.pk = pk;
            this.get_meeting_info();
        }

        // Set site select options
        var sites = this.get_site_select_data();
        this.site_select.data = sites;
        this.site_select.initialize();
        var first_site_value = this.site_select.element.find('.option').first().find('input').val();
        this.site_select.set_value(first_site_value);

        this.element.addClass('show');
        this.attendance.element.addClass('modal-shadow');
        this.get_user_filtersets();
    }

    hide() {
        this.element.removeClass('show');
        this.attendance.element.removeClass('modal-shadow');
    }

    get_meeting_info() {

    }

    initialize_form() {

    }

    submit_form() {
        console.log($("#id_type").val());
//        var set_files = (this.base_info.hasOwnProperty("pk")) ? this.base_info["pk"] : null;
        var data = this.file_input.form_data;
//        var delete_files = JSON.stringify(this.file_input.delete_files);
//        var set_files = (this.base_info.hasOwnProperty("pk")) ? this.base_info["pk"] : null;
//        data.append('delete_files', delete_files);
//        data.append('set_files', set_files)
        data.append('form', this.form.element.serialize());
        data.append('dates', JSON.stringify(this.date_select.value));
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

    submit_success(data) {
        this.element.trigger(":update");
        console.log(data);
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
        this.element.find('.back').click({func: this.hide, object: this}, this.dispatch);
        this.element.find('#attendance_btn').click({func: this.attendance.toggle, object: this.attendance}, this.dispatch);
        this.element.find('#meeting_submit_btn').click({func: this.submit_form, object: this}, this.dispatch);
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
        if ($(element).hasClass('calendar-meeting')) {
            var pk = $(element).attr('data-pk');
        }
        this.meeting_info.show(pk);
    }

    make_meeting_text_color(color_str) {
        var s = (parseInt(color_str.slice(10,12),10) + 20).toString();
        var l = (parseInt(color_str.slice(15,17),10) - 35).toString();
        var a = 1.0.toString();
        var hsla = color_str.slice(0,10) + s + '%, ' + l + '%, ' + a + ')';
        return hsla;
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
                    .addClass('calendar-meeting')
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
        this.site_select.element.on(":change", {func: this.reload_month, object: this}, this.dispatch);
        this.meeting_info.element.on(":update", {func: this.reload_month, object: this}, this.dispatch);
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