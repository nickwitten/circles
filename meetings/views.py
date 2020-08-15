from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
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
    form = forms.MeetingCreationForm(user=request.user)
    context = {
        'form': (form, form.get_fields()),
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
    meeting = get_object_or_404(models.Meeting, pk=pk)
    if meeting not in request.user.userinfo.user_meeting_access():
        raise PermissionDenied('Access Denied')
    saved_lists = meeting.attendance_lists.all()
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
        'people': people,
        'meeting_data': meeting.to_dict() if meeting else None,
    }
    return JsonResponse(data)

def post_meeting_info(request, pk):
    if not request.user.is_authenticated:
        raise Http404()
    if request.method == 'POST':
        form_dict = QueryDict(request.POST.get('form'))
        dates = json.loads(request.POST.get('dates'))
        files = request.FILES
        delete_files = request.POST.get('delete_files', None)
        files['delete_files'] = json.loads(delete_files) if delete_files else None
        base_meeting = None
        if pk:
            files['set_files'] = pk
            meeting = models.Meeting.objects.get(pk=pk)
            form = forms.MeetingCreationForm(form_dict, user=request.user, instance=meeting)
            if form.is_valid():
                base_meeting = form.save()
                base_meeting.save(files=files)
                dates.pop(0)
            else:
                return JsonResponse({})
        created_meetings = []
        for date in dates:
            form = forms.MeetingCreationForm(form_dict, user=request.user)
            if form.is_valid():
                meeting = form.save(commit=False)
                # Change Date
                year = int(date[0:4])
                month = int(date[5:7])
                day = int(date[8:])
                meeting.start_time = meeting.start_time.replace(month=month, day=day, year=year)
                meeting.end_time = meeting.end_time.replace(month=month, day=day, year=year)
                meeting.save(files=files)
                created_meetings += [meeting]
            else:
                return JsonResponse({})
        data = base_meeting.to_dict() if base_meeting else created_meetings[0].to_dict()
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

