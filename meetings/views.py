from django.http import JsonResponse
from django.shortcuts import render
import datetime
from . import models
from . import forms

def meetings(request):
    context = {
        'form': forms.MeetingCreationForm
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

def get_meeting_info(request):
    pk = request.GET.get('pk')
    meeting = models.Meeting.objects.get(pk=pk)
    data = {
        'pk': meeting.pk,
        'title': meeting.title,
        'start_time': meeting.start_time,
        'end_time': meeting.end_time,
    }
    return JsonResponse(data)

def post_meeting_info(request, pk):
    if request.method == 'POST':
        if pk:
            meeting = models.Meeting.objects.get(pk=pk)
            form = forms.MeetingCreationForm(request.POST, instance=meeting)
        else:
            form = forms.MeetingCreationForm(request.POST)
        if form.is_valid():
            form.save()
        data = {}
        return JsonResponse(data)