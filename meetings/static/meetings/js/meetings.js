/////////////// HTML Elements ///////////////////

function addWeekHTML(days) {
    ///// Calendar Week HTML ////////
    var week = $('<ul/>')
        .addClass('calendar-week');
    for (var i=0; i<days.length; i++) {
        /////// Day Box HTML /////////
        var day = $('<li/>')
            .addClass('calendar-day');
        //// Month Number HTML ////
        var day_monthnum = $('<p/>')
            .text(days[i]['monthnum'])
            .addClass('monthnum')
        day.append(day_monthnum);
        /////// Meetings HTML //////
        var meetings_container = $('<div/>')
            .addClass('meetings-container');
        for (var j=0; j<days[i]['meetings'].length; j++) {
            meeting = $('<div/>')
                .addClass('calendar-meeting')
                .attr('data-pk', days[i]['meetings'][j][2]);
            meeting.append($('<p/>')
                .text(days[i]['meetings'][j][0])
                .addClass('meeting-description'));
            meetings_container.append(meeting);
        }
        day.append(meetings_container);
        var spacer = $('<div/>')
            .addClass('spacer')
            .text('spacer');
        day.append(spacer);
        week.append(day);
    }
    $('#days_container').append(week);
}

function addHeaderHTML(month, year) {
    month = $('<h3/>')
        .text(month);
    year = $('<p/>')
        .text(year);
    $('#month_container').append(month)
    $('#year_container').append(year)
}

/////////////////////////////////////////////////
var meetings;
var monthOffset = 0;

$(document).ready(function(){
    buildCalendar(monthOffset, null);
    startListeners();
});

// parameters:
    // month_offset is from current date
    // step:
        // 1 is get next from month_offset
        // -1 is get previous from month_offset
        // 0 is get month_offset
function buildCalendar(month_offset, step) {
    $('#month_container').html(null);
    $('#year_container').html(null);
    $('#days_container').html(null);
    var dates = getDates(month_offset + step);
    var view = dates[2];
    addHeaderHTML(view.format('MMMM'), view.format('YYYY'));
    var current_date = dates[1];
    dates = dates[0];

    // True means meetings were queried and rest was handled by success
    if (!checkMeetingQuery(month_offset, step, current_date[0], current_date[1], dates, view)) {
        addDays(dates, view);
        startCalendarListeners();
    }
}

// query for selected meeting and get filled meeting form
// pk = null get uninitialized meeting form
// construct the html to display all fields
function buildMeetingInfo (pk) {
    showMeetingInfo();
    if (pk) {
        getMeetingInfo(pk);
    }
}

function submitMeeting(pk) {
    form = $("#meeting_form").serialize();
    $.ajax({
        url: 'post-meeting-info/' + pk,
        data: form,
        type: 'post',
        success: function(data) {
            buildCalendar(monthOffset, 0);
        }
    })
}

// Returns a list of month days that need to be added,
// current date in (year, month, day) or null if not in current view,
// month and year of current view

function getDates(month_offset) {
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

function floorbase32(int) {
    return Math.floor(int / 32) * 32;
}

function checkMeetingQuery(month_offset, step, current_year, current_month, dates, view) {
    var meetings_basemonthoffset = floorbase32(month_offset + step + 16) - 16;
    if (floorbase32(month_offset + 16) - 16 != meetings_basemonthoffset || !step) {
        var current_date = moment().year(current_year).month(current_month-1);
        var base_date = current_date.add(meetings_basemonthoffset - 1, 'month');
        var baseyear = base_date.format('YYYY');
        var basemonth = base_date.format('MM');
        var end_date = base_date.add(32 + 2, 'month');
        var endyear = end_date.format('YYYY');
        var endmonth = end_date.format('MM');
        queryMeetingsDb(baseyear, basemonth, endyear, endmonth, dates, view);
        return true
    }
    return false
}

function queryMeetingsDb(baseyear, basemonth, endyear, endmonth, dates, view) {
    var data = {
        'baseyear': baseyear,
        'basemonth': basemonth,
        'endyear': endyear,
        'endmonth': endmonth,
    }
    $.ajax({
        url: "get-meetings",
        data: data,
        method: 'GET',
        success: function(data) {
            meetings = {};
            for (var i=0; i<data.meetings.length; i++) {
                meeting = data.meetings[i];
                obj = moment.parseZone(meeting['start_time']);
                date = obj.format('DD-MM-YYYY');
                time = obj.format('HH-mm');
                try {
                    meetings[date].push([meeting['title'], time, meeting['pk']]);
                } catch(err) {
                    meetings[date] = [[meeting['title'], time, meeting['pk']], ];
                }
            }
            addDays(dates, view);
            startCalendarListeners();
        }
    });
}

function addDays(dates, view) {
    var i = 0;
    for (i; i<(dates.length/7); i++) {
        var j = 0;
        var days = []
        for (j; j<7; j++) {
            view_moment = view.clone();
            var monthnum = dates[(i*7) + j];
            // Check for meetings on this day
            if (i == 0 && monthnum > 7) {
                day = view_moment.add(-1, 'month').format('-MM-YYYY');
            } else if (i > 3 && monthnum < 7) {
                day = view_moment.add(1, 'month').format('-MM-YYYY');
            } else {
                day = view_moment.format('-MM-YYYY');
            }
            day = monthnum.toString().padStart(2, '0') + day;
            var found_meetings = meetings[day];
            if (!found_meetings) {
                found_meetings = [];
            }
            var day = {monthnum: monthnum, meetings: found_meetings};
            days.push(day);
        }
        addWeekHTML(days);
    }
}

function getMeetingInfo(pk) {
    var data = {'pk':pk};
    var data_outer = null;
    $.ajax({
        url: "get-meeting-info",
        data: data,
        method: 'GET',
        success: function(data) {
            initializeForm(data);
        }
    });
}

function initializeForm(meeting) {
    $('#id_title').val(meeting.title);
    $('#id_start_time').val(meeting.start_time);
    $('#id_end_time').val(meeting.end_time);
    $('#meeting_submit_btn').attr('data-pk', meeting.pk);
}

function showMeetingInfo() {
    document.getElementById('meeting_info_container').classList.add('show');
}

function hideMeetingInfo() {
    document.getElementById('meeting_info_container').classList.remove('show');
}
function startCalendarListeners() {
    $(".calendar-meeting").on("click", function() {
        buildMeetingInfo($(this).attr("data-pk"));
    });
    $("#meeting_back_btn").on("click", function() {
        hideMeetingInfo();
    });
}
function startListeners() {
    $("#meeting_submit_btn").on("click", function() {
        submitMeeting($(this).attr("data-pk"));
    });
}