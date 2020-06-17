/////////////// HTML Elements ///////////////////

function addWeekHTML(days, include_site) {
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
            meeting_info = days[i]['meetings'][j];
            color = meeting_info['color'];
            text_color = make_text_color(color);
            meeting = $('<div/>')
                .addClass('calendar-meeting')
                .css('background-color', color)
                .attr('data-pk', meeting_info['pk'])
                .attr('data-sitepk', meeting_info['site']);
            title = $('<p/>')
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
    $('#days_container').append(week);
}

function addSelectorWeekHTML(days, selected, inactive) {
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
            day.on("click", function() {selectDate($(this))});
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

function addPeopleHTML(people, people_pks) {
    for (var i=0; i<people.length; i++) {
        item = $('<div/>')
            .addClass('attendance-item')
            .attr("data-pk", people_pks[i])
        item.append(
            $('<input/>')
                .attr('type', 'checkbox')
        );
        item.append(
            $('<p/>')
                .text(people[i])
                .attr('data-pk', people_pks[i])
        );
        $('#people_select').append(item);
    }
}

// files: (file title, file object pk, file location)
// dlt_btn: boolean to include delete button on file
function addFileHTML(files, dlt_btn) {
    for (var i=0; i<files.length; i++) {
        file = $('<div/>')
            .addClass('file')
            .attr('data-pk', files[i][1]);
        title = $('<a/>')
            .text(files[i][0])
            .attr('href', files[i][2])
            .addClass('blacklink');
        delete_btn = $('<i/>')
            .addClass('fas fa-times delete')
            .on("click", function() {confirmFileDelete($(this).parent().attr('data-pk'))})
        file.append(title);
        if (dlt_btn) {
            file.append(delete_btn);
            // Only open new tab if dlt_btn
            title.attr('target', '_blank');
        }
        $('#files').append(file);
    }
}

function addLinkHTML(name, url) {
        var link = $('<div/>')
            .addClass('link')
        var name = $('<a/>')
            .text(name)
            .attr('href', url)
            .attr('target', '_blank')
            .addClass('blacklink');
        var delete_btn = $('<i/>')
            .addClass('fas fa-times delete')
            .on("click", function() {deleteMeetingLink($(this).parent().find('a'))})
        link.append(name);
        link.append(delete_btn);
        $('#links').append(link);
}

function addAlertHTML(message) {
    alert = $('<div/>')
        .addClass('alert alert-danger')
        .text(message);
    close_btn = $('<a/>')
        .attr('href','#')
        .addClass('close fas fa-times')
        .attr('data-dismiss', 'alert')
        .attr('aria-label','close');
    alert.append(close_btn);
    $('.alert-container').append(alert);
}

function addMeetingSiteOptionHTML(site, site_pk) {
    console.log(site);
    console.log(site_pk);
    option = $('<option/>')
        .text(site)
        .val(site_pk)
    $('#id_site').append(option);
}
/////////////////////////////// Globals //////////////////////////////////////////

var meetings;
var monthOffset = 0;
var datePickerSelectedDates = [];

////////////////////////// Top Level Functions ///////////////////////////////////

$(document).ready(function(){
    buildCalendar(monthOffset, null);
    startListeners();
    setColorSelect('hsla(0.0, 93%, 64%, 0.3)');
    showSites($('#calendar_menu .site_select').children().eq(1));
    $('#id_type').attr('readonly', 'readonly');
    $('#id_links').val('[]');
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
        date = month + '/' + day + '/' + year
        $('#date').text(date);
        datePickerSelectedDates.push(date);
        $('#date_select_btn').attr('data-month_offset',monthOffset);
    }
}


function submitMeeting(pk) {
    datetimes = getDatetimes();
    start_datetime = datetimes[0];
    end_datetime = datetimes[1];
    $('#id_color').val($('#color_select').attr('data-color'));
    $('#id_attendance_lists').val(getListSelectValue());
    $('#id_attendees').val(getPeopleSelectValue());
    $('#id_start_time').val(start_datetime);
    $('#id_end_time').val(end_datetime);
    $('#date_select').hide();
    var form = $("#meeting_form").serialize();
    var csrftoken = $('[name = "csrfmiddlewaretoken"]').val();
    dates = JSON.stringify(datePickerSelectedDates);
    $.ajax({
        url: 'post-meeting-info/' + pk,
        headers: {
            'X-CSRFToken': csrftoken,
        },
        data: {
            'form':form,
            'dates':dates,
        },
        type: 'post',
        success: function(data) {
            $('#meeting_submit_btn').attr('data-pk', data.pks[0]);
            // If new meeting(s) created handle files
            if (pk == 0) {
                // upload new files to each created meeting
                // first clear temporary file html elements
                $('#files').html(null);
                for (var i=0; i<data.pks.length; i++) {
                    uploadMeetingFiles(data.pks[i], $('#file_upload')[0].files);
                }
            }
            // Form was invalid
            console.log(data.pks);
            if (data.pks[0] == 0) {
                addAlertHTML('Invalid meeting input')
            }
            // Update Calendar
            buildCalendar(monthOffset, 0);
            // Update Date on Meeting
            datePickerSelectedDates = datePickerSelectedDates.slice(0,1);
            $('#date').text(datePickerSelectedDates[0]);
        }
    })
}

function deleteMeeting(pk) {
    if ($('#meeting_submit_btn').attr('data-pk') == 0) {
        hideMeetingInfo();
        return
    }
    var csrftoken = $('[name = "csrfmiddlewaretoken"]').val();
    $.ajax({
        url: 'delete/' + pk,
        headers: {
            'X-CSRFToken': csrftoken,
        },
        method: 'POST',
        success: function() {
            hideMeetingInfo();
            buildCalendar();
        }
    });
}

function selectSite(selected) {
    // ALL was selected
    if (selected.parent().hasClass('all')) {
        if (selected.is(':checked')) {
            $('#calendar_menu .site_select').children().each(function() {
                $(this).find('input').prop('checked', true);
            });
        } else {
            $('#calendar_menu .site_select').children().each(function() {
                $(this).find('input').prop('checked', false);
            });
        }
    }

    // Full chapter was selected
    if (selected.parent().hasClass('chapter')) {
        if (selected.is(':checked')) {
            selected.parent().children().each(function() {
                $(this).find('input').prop('checked', true);
            });
        } else {
            selected.parent().children().each(function() {
                $(this).find('input').prop('checked', false);
            });
        }
    }

    // Site was selected
    if (selected.parent().hasClass('site')) {
        allChecked = true;
        selected.parents('.sites').children().each(function() {
            if (!($(this).find('input').is(':checked'))) {
                allChecked = false;
            }
        });
        if (allChecked) {
            selected.parents('.chapter').children('input').prop('checked', true);
        } else {
            selected.parents('.chapter').children('input').prop('checked', false);
        }
    }

    // Check to see if all chapters are selected
    allChecked = true
    $('#calendar_menu .site_select').children('.chapter').each(function() {
        if (!($(this).find('input').is(':checked'))) {
            allChecked = false;
        }
    })
    if (allChecked) {
        $('#calendar_menu .site_select').find('.all input').prop('checked', true);
    } else {
        $('#calendar_menu .site_select').find('.all input').prop('checked', false);
    }

    buildCalendar(monthOffset);
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
    var sites = []
    $('#calendar_menu .site_select').find('.site input').each(function() {
        if ($(this).is(':checked')) {
            sites.push($(this).attr('data-pk'));
        }
    });
    sites = JSON.stringify(sites);
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
        success: function(data) {
            meetings = {};
            for (var i=0; i<data.meetings.length; i++) {
                meeting = data.meetings[i];
                obj = moment.parseZone(meeting['start_time']);
                date = obj.format('DD-MM-YYYY');
                time = obj.format('HH-mm');
                try {
                    meetings[date].push(meeting);
                } catch(err) {
                    meetings[date] = [meeting];
                }
            }
            addDays(dates, view);
            startCalendarListeners();
        }
    });
}

function uploadMeetingFiles(pk, files) {
    if ($('#meeting_submit_btn').attr('data-pk') == 0) {
        // Meeting hasn't been created.  Files will be uploaded on creation.
        // In meantime add file html
        files_info = []
        for (var i=0; i<files.length; i++) {
            files_info.push([files[i].name , 0, '#']);
        }
        $('#files').html(null);
        addFileHTML(files_info, false);
        return
    }
    var data = new FormData();
    for (var i=0; i<files.length; i++) {
        data.append(files[i].name, files[i]);
    }
    var csrftoken = $('[name = "csrfmiddlewaretoken"]').val();
    $.ajax({
        url: "meeting-files/" + pk,
        headers: {
            'X-CSRFToken': csrftoken,
        },
        data: data,
        method: 'POST',
        processData: false,
        contentType: false,
        success: function(data) {
            if ($('#meeting_submit_btn').attr('data-pk') == pk) {
                addFileHTML(data.files.slice(0,files.length), true);
            }
        }
    })
}

function confirmFileDelete(pk) {
    $('#file_confirm_delete .delete-btn').attr('data-pk', pk);
    $('#file_confirm_delete').show();
}

function deleteMeetingFile(pk) {
    var csrftoken = $('[name = "csrfmiddlewaretoken"]').val();
    $.ajax({
        url: "meeting-files/0",
        headers: {
            'X-CSRFToken': csrftoken,
        },
        data: {
            'file_pk': pk,
        },
        method: 'POST',
        success: function(data) {
            $('#files').children().each(function() {
                if ($(this).attr('data-pk') == pk.toString()) {
                    $(this).remove();
                }
            })
        }
    })
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
            active = true;
            if ((i==0 && monthnum>7) || (i==dates.length/7-1 && monthnum<7)) {
                active = false;
            }
            var day = {monthnum: monthnum, meetings: found_meetings, active: active};
            days.push(day);
        }
        site_ct = 0;
        $('#calendar_menu .site_select').find('input').each(function () {
            site_ct += ($(this).is(':checked')) ? 1 : 0;
        });
        include_site = (site_ct > 1) ? true : false;
        addWeekHTML(days, include_site);
    }
}


//// Building Meeting Info

// If lists is provided only update people select
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
    setPeopleSelectValue(meeting.attendees);
    if (!update_only_people_select) {
        $('#id_type').val(meeting.type);
        $('#date').text(meeting.start_date);
        datePickerSelectedDates.push(meeting.start_date);
        $('#date_select_btn').attr('data-month_offset', monthOffset);
        setListSelectValue(meeting.attendance_lists);
        setTimeSelectValue(meeting.start_time, meeting.end_time);
        setColorSelect(meeting.color);
        $('#start_time').val(meeting.start_time.slice(0,2));
        $('#end_time').val(meeting.end_time.slice(0,2));
        $('#id_site').val(meeting.site);
        $('#id_location').val(meeting.location);
        $('#id_notes').val(meeting.notes);
        $('#id_links').val(meeting.links);
        setMeetingLinks(meeting.links);
        addFileHTML(meeting.files, true);
        $('#meeting_submit_btn').attr('data-pk', meeting.pk);
        expandTitle();
    }
}

function showMeetingInfo() {
    document.getElementById('meeting_info_container').classList.add('show');
    $('#attendance_container').css('box-shadow', '0 0 0 999em rgba(0, 0, 0, 0.41)');
    getUserFilterSets();
    // update meeting form's site select
    $('#id_site').html(null);
    $('#calendar_menu .site_select').find('.site').each(function() {
        if ($(this).find('input').is(':checked')) {
            site = $(this).find('.site-name');
            console.log(site);
            addMeetingSiteOptionHTML(site.text(), site.attr('data-pk'));
        }
    });
}

function hideMeetingInfo() {
    document.getElementById('meeting_info_container').classList.remove('show');
    $('#attendance_container').css('box-shadow','');
    $('#attendance_container').css('left','-100%');
    $('#id_type').val('');
    $('#type_select').removeClass('visible');
    $('#type_select .container').removeClass('show');
    $('#id_start_time').val('');
    datePickerSelectedDates = [];
    $('#date_select').hide();
    $('#date_container').removeClass('shadow');
    $('#id_end_time').val('');
    $('#start_hour').text('00');
    $('#start_minute').text('00');
    $('#start_period').text('p.m.');
    $('#end_hour').text('00');
    $('#end_minute').text('00');
    $('#end_period').text('p.m.');
    $('#id_site').val('');
    $('#id_location').val('');
    $('#id_notes').val('');
    $('#id_links').val('[]');
    $('#links').html(null);
    $('.time-container').children().val('');
    $('#colors').hide();
    $('#id_attendance_lists').val('');
    $('#id_attendees').val('');
    $('.lists').html(null);
    $('#people_select').html(null);
    $('#files').html(null);
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
    $('.expanding_size').text('Type'); // Expand to see the placeholder
  }
}

function setColorSelect(color) {
    $('#color_select').css('background-color', color.slice(0,20) + '0.7');
    $('#color_select').attr('data-color',color);
    $('#colors > div').each(function() {
        color = $(this).attr('data-color');
        bold_color = color.slice(0, 20) + '0.7)';
        $(this).css('background-color', bold_color);
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
        // check if the date has been selected
        selected = []
        inactive = []
        for (var j=0; j<7; j++) {
            month_str = month;
            day = dates[i*7+j].toString();
            day = (day.length == 1) ? '0'+day : day;
            if (i==0 && parseInt(day) > 7) {
                month_str = (parseInt(month)-1).toString();
                inactive.push(j);
            } else if (i==(dates.length/7-1) && parseInt(day) < 7) {
                month_str = (parseInt(month)+1).toString();
                inactive.push(j);
            }
            date = month_str + '/' + day + '/' + year;
            if (datePickerSelectedDates.includes(date)) {
                selected.push(j)
            };
        }
        addSelectorWeekHTML(dates.slice(i*7,i*7+7), selected, inactive);
    }
}

function toggleDatePicker(month_offset) {
    $('#date_select').toggle();
    $('#date_container').toggleClass('shadow');
    $('#date_select_btn').toggleClass('hidden');
    buildDatePicker(month_offset);
}

function selectDate(dayHTML) {
    var day = dayHTML.children().text()
    day = (day.length < 2) ? '0'+day : day; // zero pad
    var month = $('#date_select_month').attr('data-number');
    var year = $('#date_select_year').text();
    var date = [month, day, year].join('/');

    if (dayHTML.hasClass('selected')) {
        dayHTML.removeClass('selected');
        datePickerSelectedDates.splice(datePickerSelectedDates.indexOf(date), 1);
    } else  {
        datePickerSelectedDates.push(date);
    }
    buildDatePicker($('#date_select_btn').attr('data-month_offset'));

    // Update date displayed
    if (datePickerSelectedDates.length > 1) {
        $('#date').text('multiple');
    } else if (datePickerSelectedDates.length == 1) {
        day = $('#date_select').find('.selected').children().text();
        day = (day.length < 2) ? '0'+day : day;
        $('#date').text([month, day, year].join('/'));
    }
}

function updateTimeSelect(classList) {
    id = classList[0].split('-').join('_');
    if (id.includes('period')) {
        period = ($('#'+id).text() == 'a.m.') ? 'p.m.' : 'a.m.';
        $('#'+id).text(period);
    } else {
        current_time = parseInt($('#'+id).text());
        if (id.includes('minute')) {
            time_difference = 10;
            time_limits = [0, 50];
        } else {
            time_difference = 1;
            time_limits = [1, 12]
        }
        current_time += (classList[2].includes('up')) ? time_difference : -time_difference;
        current_time = (current_time < time_limits[0]) ? time_limits[1] : current_time;
        current_time = (current_time > time_limits[1]) ? time_limits[0] : current_time;
        current_time = (current_time == 0) ? '00' : current_time;
        $('#'+id).text(current_time);
    }
}

function getDatetimes() {
    start_date = (datePickerSelectedDates.length <= 1) ? $('#date').text() : datePickerSelectedDates[0];
    start_period = $('#start_period').text();
    start_hour = $("#start_hour").text();
    start_hour = (start_period == 'p.m.') ? parseInt(start_hour) + 12 : start_hour;
    start_minute = $('#start_minute').text();
    start_datetime = start_date + ' ' + start_hour + ':' + start_minute + ':00';
    end_period = $('#end_period').text();
    end_hour = $("#end_hour").text();
    end_hour = (end_period == 'p.m.') ? parseInt(end_hour) + 12 : end_hour;
    end_minute = $('#end_minute').text();
    end_datetime = start_date + ' ' + end_hour + ':' + end_minute + ':00';
    return [start_datetime, end_datetime]
}

function setTimeSelectValue(start_time, end_time) {
    start_period = end_period = 'a.m.';
    start_hour = parseInt(start_time.slice(0,2));
    end_hour = parseInt(end_time.slice(0,2));
    if (start_hour >= 12) {
        start_period = 'p.m.';
        start_hour -= 12;
    }
    if (end_hour >= 12) {
        end_period = 'p.m.';
        end_hour -= 12;
    }
    $('#start_hour').text(start_hour);
    $('#start_minute').text(start_time.slice(3,5));
    $('#start_period').text(start_period);
    $('#end_hour').text(end_hour);
    $('#end_minute').text(end_time.slice(3,5));
    $('#end_period').text(end_period);
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

function setPeopleSelectValue(people) {
    $('#people_select').children().each(function() {
        if (people.includes(parseInt($(this).find('p').attr('data-pk')))) {
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

function getPeopleSelectValue() {
    var people = [];
    $('#people_select').children().each(function() {
        if ($(this).find('input').is(":checked")) {
            people.push($(this).find('p').attr('data-pk'));
        }
    });
    return people
}

function showSites(chapter) {
    $('#calendar_menu .site_select').children().each(function() {
        $(this).find('.sites').hide();
        $(this).removeClass('shadow')
    })
    chapter.addClass('shadow');
    chapter.find('.sites').show();
}

function selectMeetingType(type) {
    $('#id_type').val('');
    if (type == 'Custom Type') {
        $('#id_type').attr('readonly', false);
        $('#id_type').focus();
        expandTitle();
    } else {
        $('#id_type').val(type);
        expandTitle();
    }
    $('#type_select .container').removeClass('show');
    $('#type_select').toggleClass('visible');
}

function setMeetingLinks(links) {
    links = JSON.parse(links);
    for (var i=0; i<links.length; i++) {
        addLinkHTML(links[i]['name'], links[i]['url']);
    }
}

function attachMeetingLink(name, url) {
    if (url.slice(0,8) != 'https://') {
        url = 'https://' + url;
    }
    var link = {'name': name, 'url': url};
    link = JSON.stringify(link);
    var current_links = $('#id_links').val()
    console.log(current_links);
    current_links = current_links.slice(0,-1)
    if (current_links.length > 1) {
        var links = current_links + ', ' + link + ']';
    } else {
        var links = current_links + link + ']';
    }
    $('#id_links').val(links);
    addLinkHTML(name, url);
}

function deleteMeetingLink(link) {
    var name = link.text();
    var url = link.attr('href');
    link.parents('.link').remove();
    var current_links = $('#id_links').val();
    current_links = JSON.parse(current_links);
    console.log(current_links);
    for (var i=0; i<current_links.length; i++) {
        if (current_links[i]['name'] == name && current_links[i]['url'] == url) {
            current_links.splice(i, 1);
            $('#id_links').val(JSON.stringify(current_links));
            return
        }
    }
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
    });
    $('.list_select').on("click", function() {
        $('.lists').toggle();
    });
    $('#attendance_back_btn').on("click", function() {
        $('#attendance_container').css('left','-100%');
        $('.lists').hide();
    });
    $('#id_type').on("click", function(event) {
        $('#type_select').toggleClass('visible');
        $('#type_select .container').toggleClass('show');
    });
    $('#id_type').on("blur", function() {
        $('#id_type').attr("readonly", "readonly");
    })
    $('#type_select .type').on("click", function() {
        selectMeetingType($(this).find('a').text());
    });
    $('#time_select i').on("click", function() {
        updateTimeSelect(this.classList);
    });
    $('#color_select').on("click", function() {
        $('#colors').toggle();
    });
    $('#color_select .color').on("click", function() {
        setColorSelect($(this).attr('data-color'));
    });
    $('#meeting_delete_btn').on("click", function() {
        $('#meeting_confirm_delete').show();
    });
    $('#meeting_confirm_delete .delete-btn').on("click", function() {
        deleteMeeting($('#meeting_submit_btn').attr('data-pk'));
        $('#meeting_confirm_delete').hide();
    });
    $('.confirm-delete .cancel-btn').on("click", function() {
        $('.confirm-delete').hide();
    });
    $('#file_upload').change(function() {
        uploadMeetingFiles($('#meeting_submit_btn').attr('data-pk'), $(this)[0].files);
    });
    $('#file_confirm_delete .delete-btn').on("click", function() {
        deleteMeetingFile($(this).attr('data-pk'));
        $('#file_confirm_delete').hide();
    });
    $('#link_upload').on("click", function() {
        $('#link_modal').show();
    });
    $('#link_modal .cancel-btn').on("click", function() {
        $('#link_name').val('');
        $('#link_url').val('');
        $('#link_modal').hide();
    });
    $('#link_modal .upload-btn').on("click", function() {
        attachMeetingLink($('#link_name').val(), $('#link_url').val());
        $('#link_name').val('');
        $('#link_url').val('');
        $('#link_modal').hide();
    });
    $('#calendar_menu_btn').on("click", function() {
        $('#calendar_menu').show();
    })
    $('#calendar_menu .back').on("click", function() {
        $('#calendar_menu').hide();
    });
    $('#calendar_menu .chapter').on("click", function() {
        showSites($(this));
    });
    $('#calendar_menu .chapter input').on("change", function() {
        selectSite($(this));
    })
    $('#calendar_menu .all input').on("change", function() {
        selectSite($(this));
    })
}
