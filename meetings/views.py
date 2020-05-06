from django.shortcuts import render
import datetime
import calendar

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
        'month': months[current_date.month-1],
        'day': current_date.day,
        'days': days,
        'events': [],
    }
    return render(request, 'meetings/meetings.html', context)
