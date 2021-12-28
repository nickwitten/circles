from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
import datetime
from meetings import models
from meetings import forms
from members.data import filter_profiles, unique_maintain_order
from members.models import FilterSet
from django.http import QueryDict
import json

@login_required
def meetings(request):
    site_access = request.user.userinfo.user_site_access_dict()
    form = forms.MeetingCreationForm(user=request.user)
    context = {
        'form': (form, form.get_fields()),
        'site_access': site_access,
    }
    return render(request, 'meetings/meetings.html', context)

@login_required
def get_meetings(request):
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

@login_required
def get_meeting_info(request):
    pk = request.GET.get('pk')
    meeting = get_object_or_404(models.Meeting, pk=pk)
    if meeting not in request.user.userinfo.user_meeting_access():
        raise PermissionDenied('Access Denied')
    data = {
        'meeting_data': meeting.to_dict() if meeting else None,
    }
    return JsonResponse(data)

@login_required
def get_members(request):
    lists = request.GET.get('lists', None)
    meeting = request.GET.get('meeting', None)
    if not lists:
        return JsonResponse({})
    lists = json.loads(lists)
    lists = [lst.filters for lst in FilterSet.objects.filter(pk__in=lists)]
    people_objs = []
    for filterset in lists:
        people_objs += filter_profiles(request.user.userinfo.user_profile_access().order_by('last_name'), json.loads(filterset))
    if meeting and int(meeting):
        meeting = request.user.userinfo.user_meeting_access().filter(pk=meeting).first()
        if not meeting:
            raise Http404
        for attendee in meeting.attendees.all().order_by('last_name'):
            people_objs += [attendee] if attendee not in people_objs else []
    people = unique_maintain_order(people_objs)
    people = [(str(profile), profile.pk) for profile in people]
    data = {
        'members': people,
    }
    return JsonResponse(data)

@login_required
def post_meeting_info(request, pk):
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
            form = forms.MeetingCreationForm(data=form_dict, user=request.user, instance=meeting)
            if form.is_valid():
                base_meeting = form.save(commit=False)
                base_meeting.save(files=files)
                form.save_m2m()
                base_meeting.train_members()
                dates.pop(0)
            else:
                return JsonResponse({})
        created_meetings = []
        for date in dates:
            form = forms.MeetingCreationForm(data=form_dict, user=request.user)
            if form.is_valid():
                meeting = form.save(commit=False)
                # Change Date
                year = int(date[0:4])
                month = int(date[5:7])
                day = int(date[8:])
                meeting.start_time = meeting.start_time.replace(month=month, day=day, year=year)
                meeting.end_time = meeting.end_time.replace(month=month, day=day, year=year)
                meeting.save(files=files)
                form.save_m2m()
                meeting.train_members()
                created_meetings += [meeting]
            else:
                return JsonResponse({})
        data = base_meeting.to_dict() if base_meeting else created_meetings[0].to_dict()
        return JsonResponse(data)

@login_required
def delete_meeting(request, pk):
    meeting = get_object_or_404(models.Meeting, pk=pk)
    if meeting.site not in request.user.userinfo.user_site_access():
        PermissionDenied('Access Denied')
    if request.method == 'POST':
        meeting.delete()
    return JsonResponse({})

