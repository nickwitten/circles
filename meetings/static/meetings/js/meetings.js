/////////////// HTML Elements ///////////////////

function addWeekHTML(days) {
    ///// Calendar Week HTML ////////
    var week = $('<ul/>')
        .addClass('calendar-week');
    for (var i=0; i<days.length; i++) {
        /////// Day Box HTML /////////
        var day = $('<li/>')
            .addClass('calendar-day');
        ////// Add Meeting Button ////
        var add_btn = $('<i/>')
            .addClass('add-meeting-btn fas fa-plus')
        day.append(add_btn);
        ///// Month Number HTML //////
        var day_monthnum = $('<p/>')
            .text(days[i]['monthnum'])
            .addClass('monthnum')
        day.append(day_monthnum);
        /////// Meetings HTML //////
        var meetings_container = $('<div/>')
            .addClass('meetings-container');
        for (var j=0; j<days[i]['meetings'].length; j++) {
            color = days[i]['meetings'][j][3]
            text_color = make_text_color(color);
            meeting = $('<div/>')
                .addClass('calendar-meeting')
                .css('background-color', color)
                .attr('data-pk', days[i]['meetings'][j][2]);
            meeting.append($('<p/>')
                .text(days[i]['meetings'][j][0])
                .css('color', text_color)
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

function addSelectorWeekHTML(days, first, last) {
    var container = $('<div/>').addClass('container');
    var week = $('<ul/>')
        .addClass('calendar-week');
    for (var i=0; i<days.length; i++) {
        /////// Day Box HTML /////////
        var day = $('<li/>')
        if ((first && days[i] > 7) || (last && days[i] < 7)) {
            var classlist = 'calendar-day inactive';
        } else {
            var classlist = 'calendar-day';
            day.on("click", function() {selectDate($(this).children().text());});
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
    $('#date_select').append(container);
}

function addSelectorHeaderHTML(month_v, month, year) {
    var header = $('<div/>')
        .addClass('border rounded')
    var monthHTML = $('<p/>')
        .attr('id', 'date_select_month')
        .attr('data-number', month)
        .text(month_v);
    var breakHTML = $('<div/>')
        .addClass('break');
    var yearHTML = $('<p/>')
        .attr('id', 'date_select_year')
        .text(year);
    var nextBtnHTML = $('<i/>')
        .addClass('next fas fa-chevron-right')
        .on("click", function() {buildDatePicker(parseInt($('#date_select_btn').attr('data-month_offset'))+1);});
    var previousBtnHTML = $('<i/>')
        .addClass('previous fas fa-chevron-left')
        .on("click", function() {buildDatePicker(parseInt($('#date_select_btn').attr('data-month_offset'))-1);});
    header.append(previousBtnHTML);
    header.append(nextBtnHTML);
    header.append(monthHTML);
    header.append(breakHTML);
    header.append(yearHTML);
    $('#date_select').append(header);
}

function addHeaderHTML(month, mnumber, year) {
    month = $('<h3/>')
        .text(month)
        .attr('data-number', mnumber);
    year = $('<p/>')
        .text(year);
    $('#month_container').append(month)
    $('#year_container').append(year)
}

function addFilterSetsHTML(filtersets) {
    for (i=0;i<filtersets.length;i++) {
        list_container = $('<div/>')
            .addClass('list_container');
        checkbox = $('<input/>')
            .attr('type', 'checkbox')
            .addClass('flex-center mr-1 ml-1');
        list_title = $('<p/>')
            .addClass('list')
            .text(filtersets[i]["title"])
            .attr("data-pk", filtersets[i]["pk"]);
        list_container.append(checkbox);
        list_container.append(list_title);
        $('#attendance_container > div > .lists').append(list_container);
    }
}

//function addFilterSetsHTML(filtersets) {
//  $('#list_select').append(
//    // disabled option that says Your Lists
//    $("<option/>")
//      .attr("selected","selected")
//      //.attr("disabled","disabled")
//      .attr("value",'0') // So can be selected on deactivation of list
//      .text("Your Lists")
//  );
//  // Add each filterset to the dropdown
//  for (i=0;i<filtersets.length;i++) {
//    $('#list_select').append(
//      $("<option/>")
//        .text(filtersets[i]["title"])
//        .attr("value",filtersets[i]["pk"])
//    );
//  }
//}

function addPeopleHTML(people, people_pks) {
    for (var i=0; i<people.length; i++) {
        $('#people_select').append(
            $('<option/>')
                .text(people[i])
                .attr("value", people_pks[i])
        );
    }
}
/////////////////////////////// Globals //////////////////////////////////////////

var meetings;
var monthOffset = 0;

////////////////////////// Top Level Functions ///////////////////////////////////

$(document).ready(function(){
    buildCalendar(monthOffset, null);
    startListeners();
    setColorSelect();
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
    addHeaderHTML(view.format('MMMM'), view.format('MM'), view.format('YYYY'));
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
function buildMeetingInfo (pk, day=null) {
    showMeetingInfo();
    if (pk) {
        getMeetingInfo(pk);
    } else {
        month = $('#month_container h3').attr('data-number');
        day = (day.length == 2) ? day : '0' + day;
        year = $('#year_container p').text();
        $('#date').text(month + '/' + day + '/' + year);
    }
}


function submitMeeting(pk) {
    start_time = $("#start_time").val()
    start_date = $('#date').text()
    start_datetime = start_date + ' ' + start_time + ':00:00';
    end_time = $("#end_time").val()
    end_datetime = start_date + ' ' + end_time + ':00:00';
    $('#id_color').val($('#color_select').val());
    $('#id_attendance_lists').val(getListSelectValue());
    $('#id_attendees').val($('#people_select').val());
    $('#id_start_time').val(start_datetime);
    $('#id_end_time').val(end_datetime);
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

///////////////////// Helper Functions /////////////////////////////

//// Building Calendar

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
                    meetings[date].push([meeting['title'], time, meeting['pk'], meeting['color']]);
                } catch(err) {
                    meetings[date] = [[meeting['title'], time, meeting['pk'], meeting['color']], ];
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


//// Building Meeting Info


function getMeetingInfo(pk, lists=null) {
    if (lists) {
        lists = JSON.stringify(lists);
    }
    var data = {'pk':pk, 'lists':lists};
    var data_outer = null;
    $.ajax({
        url: "get-meeting-info",
        data: data,
        method: 'GET',
        success: function(data) {
            if (lists == null) {
                initializeForm(data, false);
            } else {
                initializeForm(data, true);
            }
        }
    });
}

function initializeForm(meeting, update_only_people_select) {
    addPeopleHTML(meeting.people, meeting.people_pks);
    $('#people_select').val(meeting.attendees)
    if (!update_only_people_select) {
        $('#id_title').val(meeting.title);
        $('#date').text(meeting.start_date)
        setListSelectValue(meeting.attendance_lists);
        $('#start_time').val(meeting.start_time.slice(0,2));
        $('#end_time').val(meeting.end_time.slice(0,2));
        $('#color_select').val(meeting.color);
        $('#meeting_submit_btn').attr('data-pk', meeting.pk);
        expandTitle();
    }
}

function showMeetingInfo() {
    document.getElementById('meeting_info_container').classList.add('show');
    $('#attendance_container').css('box-shadow', '0 0 0 999em rgba(0, 0, 0, 0.41)');
    getUserFilterSets();
}

function hideMeetingInfo() {
    document.getElementById('meeting_info_container').classList.remove('show');
    $('#attendance_container').css('box-shadow','');
    $('#attendance_container').css('left','-100%');
    $('#id_title').val('');
    $('#id_start_time').val('');
    $('#id_end_time').val('');
    $('.time-container').children().val('');
    $('#id_attendance_lists').val('');
    $('#id_attendees').val('');
    $('.lists').html(null);
    $('#people_select').html(null);
    $('#meeting_submit_btn').attr('data-pk', 0);
    $('.lists').hide()
    expandTitle();
}

function getUserFilterSets() {
  var filterset_select_element = $("#list_select")
  filterset_select_element.html(null); // Clear the drop down
  // Retrieve the user's filtersets
  $.ajax({
    url: "/members/profile/get-filtersets",
    dataType: 'json',
    success: function (data) {
      // Data contains list of filterset objects which contain
      // a title and a list of filter objects
      addFilterSetsHTML(data.filtersets); // Add the html elements
    },
  });
};


//// Update Meeting Info

function updatePeopleSelect() {
    $('#people_select').html('');
    lists = getListSelectValue();
    getMeetingInfo($('#meeting_submit_btn').attr('data-pk'), lists);
}

function expandTitle() {
  $('.expanding_size').text($('.expanding_input').val()); // Copy text to the span element
  if ($('.expanding_input').val() == '') { // When expanding_input is empty
    $('.expanding_size').text('Title'); // Expand to see the placeholder
  }
}

function setColorSelect() {
    $('#color_select > option').each(function() {
        $(this).css('background-color', $(this).val());
    });
}

function make_text_color(color_str) {
    s = (parseInt(color_str.slice(10,12),10) + 20).toString();
    l = (parseInt(color_str.slice(15,17),10) - 35).toString();
    a = 1.0.toString();
    hsla = color_str.slice(0,10) + s + '%, ' + l + '%, ' + a + ')';
    return hsla;
}

function buildDatePicker(month_offset) {
    $('#date_select').html('');
    $('#date_select_btn').attr('data-month_offset', month_offset);
    var dates = getDates(month_offset);
    var month_v = dates[2].format('MMMM');
    var month = dates[2].format('MM');
    var year = dates[2].format('YYYY');
    dates = dates[0];
    addSelectorHeaderHTML(month_v, month, year);
    for (var i=0; i<(dates.length/7); i++) {
        addSelectorWeekHTML(dates.slice(i*7,i*7+7), i==0, i+1==dates.length/7);
    }
}

function toggleDatePicker(month_offset) {
    $('#date_select').toggle();
    $('#date_container').toggleClass('shadow');
    $('#date_select_btn').toggleClass('hidden');
    buildDatePicker(month_offset);
}

function selectDate(day) {
    var month = $('#date_select_month').attr('data-number');
    var year = $('#date_select_year').text();
    $('#date').text(month + '/' + day + '/' + year);
    toggleDatePicker($('date_select_btn').attr('data-month_offset'));
}

function addAttendance() {
    $('#attendance_container').css('left','50%');
}

function setListSelectValue(lists) {
    $('.lists').children().each(function() {
        if (lists.includes(parseInt($(this).find('p').attr('data-pk')))) {
            $(this).find('input').prop('checked',true);
        }
    });
}

function getListSelectValue() {
    var lists = [];
    $('.lists').children().each(function() {
        if ($(this).find('input').is(":checked")) {
            lists.push($(this).find('p').attr('data-pk'));
        }
    });
    return lists
}

//// Listeners

function startCalendarListeners() {
    $(".calendar-meeting").on("click", function() {
        buildMeetingInfo($(this).attr("data-pk"));
    });
    $("#meeting_back_btn").on("click", function() {
        hideMeetingInfo();
    });
    $(".add-meeting-btn").on("click", function() {
        buildMeetingInfo(0, $(this).parent().find('.monthnum').text());
    });
}
function startListeners() {
    $("#meeting_submit_btn").on("click", function(event) {
        event.preventDefault();
        submitMeeting($(this).attr("data-pk"));
    });
    $(".lists").on("click",function() {
        updatePeopleSelect();
    });
    $("#date_select_btn").on("click", function() {
        toggleDatePicker(parseInt($(this).attr('data-month_offset')));
    });
    $('#attendance_btn').on("click", function() {
        event.preventDefault();
        addAttendance();
    })
    $('.list_select').on("click", function() {
        $('.lists').toggle();
    });
    $('#attendance_back_btn').on("click", function() {
        $('#attendance_container').css('left','-100%');
        $('.lists').hide();
    });
}
