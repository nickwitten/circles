from django.http import JsonResponse
from django.shortcuts import render
import datetime
import calendar
from . import models

def meetings(request):
    months = [
        'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
        'November', 'December'
    ]
    current_date = datetime.datetime.now()
    cal = calendar.Calendar()
    month_iter = cal.itermonthdates(year=current_date.year, month=current_date.month)
    days = []
    try:
        while True:
            date_obj = next(month_iter)
            days += [date_obj.day]
    except:
        pass
    # TODO: Query events from database
    context = {
        'year': current_date.year,
        'month': months[current_date.month-1],
        'day': current_date.day,
        'days': days,
        'events': [],
    }
    return render(request, 'meetings/meetings.html', context)


def get_meetings(request):
    baseyear = int(request.GET.get('baseyear'))
    basemonth = int(request.GET.get('basemonth'))
    endyear = int(request.GET.get('endyear'))
    endmonth = int(request.GET.get('endmonth'))
    start_date = datetime.date(baseyear, basemonth, 1)
    end_date = datetime.date(endyear, endmonth, 1)
    meetings = models.Meeting.objects.filter(start_time__range=(start_date, end_date))
    meetings = meetings.values('title', 'start_time', 'end_time', 'pk')
    print(meetings)
    data = {
        'meetings': list(meetings),
    }
    return JsonResponse(data)
