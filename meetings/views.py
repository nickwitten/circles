import os

from django.http import JsonResponse
import json
from django.shortcuts import render
import datetime
from . import models
from . import forms
from members.data import filter_profiles
from members.models import Profile, FilterSet
from django.http import QueryDict
from django.http import FileResponse
from circles import settings

def meetings(request):
    context = {
        'form': forms.MeetingCreationForm,
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
    meeting = models.Meeting.objects.filter(pk=pk).first()
    if meeting:
        start_date = meeting.start_time.date().strftime('%m/%d/%Y')
        start_time = meeting.start_time.time().strftime('%H:%M:%S')
        end_time = meeting.end_time.time().strftime('%H:%M:%S')
        saved_lists = meeting.attendance_lists.all()
        list_pks = [list.pk for list in saved_lists]
        attendees = [attendee.pk for attendee in meeting.attendees.all()]
        title = meeting.title
        color = meeting.color
        files = [(MeetingFile.title, MeetingFile.pk, settings.MEDIA_URL + MeetingFile.file.name) for MeetingFile in meeting.files.all()]
    else:
        attendees = []
        pk = title = start_date = start_time = end_time = list_pks = color = files = None
    if not lists:
        lists = [list.filterset for list in saved_lists]
    else:
        lists = [int(pk) for pk in json.loads(lists)]
        lists = [list.filterset for list in FilterSet.objects.filter(pk__in=lists)]
    people_objs = []
    for filterset in lists:
        people_objs += filter_profiles(Profile.objects.all(), json.loads(filterset))
    people = list(set([str(profile) for profile in people_objs]))
    people_pks = list(set([profile.pk for profile in people_objs]))
    data = {
        'pk': pk,
        'title': title,
        'start_date': start_date,
        'start_time': start_time,
        'end_time': end_time,
        'attendance_lists': list_pks,
        'attendees': attendees,
        'people': people,
        'people_pks': people_pks,
        'color': color,
        'files': files,
    }
    return JsonResponse(data)

def post_meeting_info(request, pk):
    if request.method == 'POST':
        form_dict = QueryDict(request.POST.get('form'))
        dates = json.loads(request.POST.get('dates'))
        meeting = None
        # Create on multiple dates
        if len(dates) > 1:
            if pk:
                models.Meeting.objects.get(pk=pk).delete()
            for date in dates:
                form = forms.MeetingCreationForm(form_dict)
                if form.is_valid():
                    meeting = form.save(commit=False)
                    month = int(date[0:2])
                    day = int(date[3:5])
                    year = int(date[6:])
                    start_time = meeting.start_time.replace(month=month, day=day, year=year)
                    end_time = meeting.end_time.replace(month=month, day=day, year=year)
                    meeting.start_time = start_time
                    meeting.end_time = end_time
                    meeting.save()
        else:

            # Update single meeting
            if pk:
                meeting = models.Meeting.objects.get(pk=pk)
                form = forms.MeetingCreationForm(form_dict, instance=meeting)
            # Create single meeting
            else:
                form = forms.MeetingCreationForm(form_dict)
            if form.is_valid():
                meeting = form.save()
        data = {'pk':meeting.pk} if meeting else {}
        return JsonResponse(data)

def meeting_files(request, pk):
    if request.method == 'POST':
        file_pk = request.POST.get('file_pk')
        # Delete file if pk in data
        if file_pk:
            MeetingFile = models.MeetingFile.objects.get(pk=file_pk)
            os.remove('/'.join([settings.MEDIA_ROOT, MeetingFile.file.name]))
            MeetingFile.delete()
            data = {
                'message': 'Deleted'
            }
        # Create new file otherwise
        else:
            files = request.FILES
            meeting = models.Meeting.objects.get(pk=pk)
            created_files = []
            for title, file in files.items():
                meeting_file = models.MeetingFile(meeting=meeting, file=file, title=title)
                meeting_file.save()
                print(meeting_file.file.name)
                created_files += [(title, meeting_file.pk, settings.MEDIA_URL + meeting_file.file.name)]
            data = {
                'files': created_files
            }
        return JsonResponse(data)
    # Serve file to client
    else:
        print('serve')

def delete_meeting(request, pk):
    if request.method == 'POST':
        models.Meeting.objects.get(pk=pk).delete()
        data = {}
    return JsonResponse(data)