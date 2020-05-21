from django.http import JsonResponse
import json
from django.shortcuts import render
import datetime
from . import models
from . import forms
from members.data import filter_profiles
from members.models import Profile, FilterSet

def meetings(request):
    context = {
        'form': forms.MeetingCreationForm,
        'times': [str(time).zfill(2) for time in range(1,25)],
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
    meetings = meetings.values('title', 'start_time', 'end_time', 'pk', 'color')
    data = {
        'meetings': list(meetings),
    }
    return JsonResponse(data)

def get_meeting_info(request):
    pk = request.GET.get('pk')
    lists = request.GET.get('lists')
    try:
        meeting = models.Meeting.objects.get(pk=pk)
    except:
        meeting = None
        print('No Meeting')
    if meeting:
        start_date = meeting.start_time.date().strftime('%m/%d/%Y ')
        start_time = meeting.start_time.time().strftime('%H:%M:%S')
        end_time = meeting.end_time.time().strftime('%H:%M:%S')
        saved_lists = meeting.attendance_lists.all()
        list_pks = [list.pk for list in saved_lists]
        attendees = [attendee.pk for attendee in meeting.attendees.all()]
    if not lists or lists == None:
        lists = [list.filterset for list in saved_lists]
    else:
        lists = [int(pk) for pk in json.loads(lists)]
        lists = [list.filterset for list in FilterSet.objects.filter(pk__in=lists)]
    people_objs = []
    for filterset in lists:
        people_objs += filter_profiles(Profile.objects.all(), json.loads(filterset))
    people = list(set([str(profile) for profile in people_objs]))
    people_pks = list(set([profile.pk for profile in people_objs]))
    if meeting:
        data = {
            'pk': meeting.pk,
            'title': meeting.title,
            'start_date': start_date,
            'start_time': start_time,
            'end_time': end_time,
            'attendance_lists': list_pks,
            'attendees': attendees,
            'people': people,
            'people_pks': people_pks,
            'color': meeting.color,
        }
    else:
        data = {
            'pk': None,
            'title': None,
            'start_time': None,
            'end_time': None,
            'attendance_lists': None,
            'attendees': None,
            'people': people,
            'people_pks': people_pks,
            'color': None,
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