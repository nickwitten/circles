from django.http import JsonResponse, Http404
from django.shortcuts import render
import datetime
from . import models
from . import forms
from members.data import filter_profiles
from members.models import FilterSet
from django.http import QueryDict
from django.core.files.base import ContentFile
from circles import settings
import json

def meetings(request):
    if not request.user.is_authenticated:
        raise Http404()
    site_access = request.user.userinfo.user_site_access_dict()
    context = {
        'form': forms.MeetingCreationForm(user=request.user),
        'site_access': site_access,
    }
    return render(request, 'meetings/meetings.html', context)


def get_meetings(request):
    if not request.user.is_authenticated:
        raise Http404()
    sites = json.loads(request.GET.get('site_pks'))
    baseyear = int(request.GET.get('baseyear'))
    basemonth = int(request.GET.get('basemonth'))
    endyear = int(request.GET.get('endyear'))
    endmonth = int(request.GET.get('endmonth'))
    start_date = datetime.date(baseyear, basemonth, 1)
    end_date = datetime.date(endyear, endmonth, 1)
    meetings = request.user.userinfo.user_meeting_access()
    meetings = meetings.filter(site__in=sites)
    meetings = meetings.filter(start_time__range=(start_date, end_date))
    meetings_info = list(meetings.values('type', 'start_time', 'end_time', 'pk', 'color'))
    for meeting, meeting_info in zip(meetings, meetings_info):
        meeting_info['site'] = str(meeting.site)
    data = {
        'meetings': meetings_info,
    }
    return JsonResponse(data)

def get_meeting_info(request):
    if not request.user.is_authenticated:
        raise Http404()
    pk = request.GET.get('pk')
    lists = request.GET.get('lists')
    meetings = request.user.userinfo.user_meeting_access()
    meeting = meetings.filter(pk=pk).first()
    if meeting:
        start_date = meeting.start_time.date().strftime('%m/%d/%Y')
        start_time = meeting.start_time.time().strftime('%H:%M:%S')
        end_time = meeting.end_time.time().strftime('%H:%M:%S')
        saved_lists = meeting.attendance_lists.all()
        list_pks = [list.pk for list in saved_lists]
        attendees = [attendee.pk for attendee in meeting.attendees.all()]
        type = meeting.type
        color = meeting.color
        site = meeting.site.pk
        location = meeting.location
        notes = meeting.notes
        files = [(MeetingFile.title, MeetingFile.pk, settings.MEDIA_URL + MeetingFile.file.name) for MeetingFile in meeting.files.all()]
        links = meeting.links
    else:
        attendees = []
        pk = type = start_date = start_time = end_time = list_pks = color = site = location = notes = links = files = None
    if not lists:
        lists = [list.filters for list in saved_lists]
    else:
        lists = [int(pk) for pk in json.loads(lists)]
        lists = [list.filters for list in FilterSet.objects.filter(pk__in=lists)]
    people_objs = []
    for filterset in lists:
        people_objs += filter_profiles(request.user.userinfo.user_profile_access(), json.loads(filterset))
    people = list(set([(str(profile), profile.pk) for profile in people_objs]))
    data = {
        'pk': pk,
        'type': type,
        'start_date': start_date,
        'start_time': start_time,
        'end_time': end_time,
        'attendance_lists': list_pks,
        'attendees': attendees,
        'people': people,
        'color': color,
        'site': site,
        'location': location,
        'notes': notes,
        'links': links,
        'files': files,
    }
    return JsonResponse(data)

def post_meeting_info(request, pk):
    if not request.user.is_authenticated:
        raise Http404()
    if request.method == 'POST':
        form_dict = QueryDict(request.POST.get('form'))
        dates = json.loads(request.POST.get('dates'))
        pks = []
        # Create on multiple dates
        if len(dates) > 1:
            old_meeting = None
            meeting_files = []
            if pk:
                old_meeting = models.Meeting.objects.get(pk=pk)
                meeting_files = old_meeting.files.all()  # Get attached files
            for i, date in enumerate(dates):
                form = forms.MeetingCreationForm(form_dict, user=request.user)
                if form.is_valid():
                    meeting = form.save(commit=False)
                    # Change Date
                    month = int(date[0:2])
                    day = int(date[3:5])
                    year = int(date[6:])
                    start_time = meeting.start_time.replace(month=month, day=day, year=year)
                    end_time = meeting.end_time.replace(month=month, day=day, year=year)
                    meeting.start_time = start_time
                    meeting.end_time = end_time
                    meeting.save()
                    pks += [meeting.pk]
                    # Copy over attached files
                    for MeetingFile in meeting_files:
                        if i:
                            title = MeetingFile.title
                            new_meeting_file = models.MeetingFile(meeting=meeting, title=title)
                            MeetingFile.file.seek(0)
                            file = ContentFile(MeetingFile.file.read())
                            file.name = MeetingFile.file.name.split('/')[-1]
                            new_meeting_file.file = file
                            new_meeting_file.save()
                        else:
                            MeetingFile.meeting = meeting
                            MeetingFile.save()
                else:
                    pks = [0]
                    break
            if old_meeting:
                old_meeting.delete()
        else:
            # Update single meeting
            if pk:
                meeting = models.Meeting.objects.get(pk=pk)
                form = forms.MeetingCreationForm(form_dict, user=request.user, instance=meeting)
            # Create single meeting
            else:
                form = forms.MeetingCreationForm(form_dict, user=request.user)
            meeting = form.save() if form.is_valid() else None
            pks = [meeting.pk] if meeting else [0]
        data = {'pks':pks}
        return JsonResponse(data)

def meeting_files(request, pk):
    if not request.user.is_authenticated:
        raise Http404()
    if request.method == 'POST':
        file_pk = request.POST.get('file_pk')
        # Delete file if pk in data
        if file_pk:
            MeetingFile = models.MeetingFile.objects.get(pk=file_pk)
            if MeetingFile.meeting.site not in request.user.userinfo.user_site_access():
                raise Http404('Access Denied')
            MeetingFile.delete_file()
            MeetingFile.delete()
            data = {
                'message': 'Deleted'
            }
        # Create new file otherwise
        else:
            meeting = models.Meeting.objects.get(pk=pk)
            if meeting.site not in request.user.userinfo.user_site_access():
                raise Http404('Access Denied')
            files = request.FILES
            created_files = []
            for title, file in files.items():
                meeting_file = models.MeetingFile(meeting=meeting, file=file, title=title)
                meeting_file.save()
                created_files += [(title, meeting_file.pk, settings.MEDIA_URL + meeting_file.file.name)]
            data = {
                'files': created_files
            }
        return JsonResponse(data)

def delete_meeting(request, pk):
    if not request.user.is_authenticated:
        raise Http404()
    meeting = models.Meeting.objects.get(pk=pk)
    if meeting.site not in request.user.userinfo.user_site_access():
        raise Http404('Access Denied')
    if request.method == 'POST':
        for MeetingFile in meeting.files.all():
            MeetingFile.delete_file()
        meeting.delete()
        data = {}
    return JsonResponse(data)

