from django.db.models.functions import Concat
from django.db.models import Value
from django.db import models
from .models import Profile, Site, Residence, Role, Training, ChildInfo, Child
import json
from io import BytesIO
import xlsxwriter

# # Types of data that need to be fetched from a residence model
# residence_data = ['first_street_address','first_city','state','zip','home_ownership','habitat_home','safe_home','repair_home']
# # Types of data that need to be fetched from a role model
# role_data = ['current_site','current_role','all_roles','current_cohort','current_resource_team','current_resource_team_role']
# # Types of data that need to be fetched from a training model
# training_data = ['excurrent_training','excurrent_not_training']
# Fields that have options in the database
model_data = (Site)

# HTML Value --> Model Field Name
keywords = {
    # Residence Data
    'first_city':'city',
    'first_state':'state',
    'first_zip':'zip',
    'first_street_address':'street_address',
    'first_home_ownership':'ownership',
    'first_habitat_home':'habitat',
    'first_safe_home':'safe',
    'first_repair_home':'repair',
    # Role Data
    'current_site':'site',
    'current_role':'position',
    'all_roles':'position',
    'current_cohort':'cohort',
    'current_resource_team':'resource_team_name',
    'current_resource_team_role':'resource_team_role',
    # Training Data
    'excurrent_training':'subject',
    'excurrent_not_training':'subject',
    # Child Data
    'all_children':'first_name'
}
# Data Fields that are in related models
residence_data = list(keywords.keys())[0:8]
role_data = list(keywords.keys())[8:14]
training_data = list(keywords.keys())[14:15]
child_data = list(keywords.keys())[16]
# HTML Value --> HTML Display
display_text = {
    'current_role':'Current Role',
    'all_roles':'All Roles',
    'current_cohort':'Cohort',
    'current_resource_team':'Resource Team',
    'current_resource_team_role':'Resource Team Role',
    'excurrent_training':'Training',
    'email':'Email',
    'cell':'Cell',
    'circles_id':'ID',
    'status':'Status',
    'birthdate':'Birthdate',
    'race':'Race',
    'gender':'Gender',
    'all_children':'Children',
    'first_street_address':'Address',
    'first_city':'City',
    'first_state':'State',
    'first_zip':'Zip',
    'first_home_ownership':'Home Ownership',
    'first_habitat_home':'Habitat Home',
    'first_safe_home':'Safe Home',
    'first_repair_home':'Repair Home',
    'current_site':'Site',
    'e_phone':'Emergency Number',
}

def field_to_model(field):
        if field in residence_data: return Residence
        elif field in role_data: return Role
        elif field in training_data: return Training
        elif field in child_data: return Child
        else: return Profile

def get_profiles(request):
    search_input = request.GET.get('search_input',None)
    sort_by = request.GET.get('sort_by',None)
    data_displayed = request.GET.get('data_displayed',None)
    data_displayed = json.loads(data_displayed)
    filters = request.GET.get('filters',None)
    filters = json.loads(filters)
    profiles = Profile.objects.all()

    profiles = search_profiles(profiles,search_input)
    profiles = filter_profiles(profiles,filters)
    profiles = get_profile_data(profiles,data_displayed)
    sorted_profiles = sort_profiles(profiles,sort_by)

    data = {
        'groups' : sorted_profiles
    }
    return data

def search_profiles(profiles,search_input):
    search = {}
    # Anotate each profile with 'firstname lastname'
    annotated_queryset = profiles.annotate(fullname = Concat('first_name', Value(' '), 'last_name'))
    # Filter out elements that don't contain search input
    profiles = annotated_queryset.filter(fullname__icontains=search_input)
    return profiles


def filter_profiles(profiles,filters):

    for filter in filters:
        filterby = filter["filterby"]
        filterinput = filter["filterinput"]
        if not filterinput: # If there is no input don't filter
            continue
        # Get model that the field is in
        model = field_to_model(filterby)
        # Get the field from the model
        field = model._meta.get_field(keywords[filterby])
        # If the field is a related model change search type
        if field.get_internal_type() == 'ForeignKey':
            search_type = '__' + keywords[filterby]
        else:
            search_type = '__icontains'
        # When the field is in the top Profile model
        if model == Profile:
            query = {}
            query[filterby + search_type] = filterinput
            profiles = profiles.filter(**query)
        # When the field is in a related model
        else:
            # Build query
            query = {}
            if filterby[0:7]=='current': query['end_date'] = None
            query[keywords[filterby] + search_type] = filterinput
            # All profiles who have an object that passes query in this List
            profile_ids = []
            for profile in profiles:
                related_models = model.objects.all().filter(profile=profile.pk)
                if 'excurrent' in filterby:
                    related_models = related_models.exclude(end_date=None)
                if 'not' in filterby and not related_models.filter(**query):
                    profile_ids.append(profile.pk)
                elif 'not' not in filterby and related_models.filter(**query):
                    profile_ids.append(profile.pk)
            # Query profiles with pk in profile_ids
            profiles = profiles.filter(pk__in=profile_ids)

    return profiles

def get_profile_data(profiles, data_displayed):
    profiles_temp = []
    for profile in profiles:
        data = []
        for data_type in data_displayed:
            data_temp = ''
            if data_type:
                model = field_to_model(data_type)
                if model == Profile:
                    value = getattr(profile,data_type)
                    if value:
                        data_temp += value
                else:
                    related_models = model.get_related(profile)
                    # Different Queries on Related Models
                    if 'first' in data_type: related_models = [related_models.first()]
                    elif 'all' in data_type: related_models = related_models
                    elif 'current' in data_type: related_models = list(related_models.filter(end_date=None))
                    elif 'excurrent' in data_type: related_models = list(related_models.exclude(end_date=None))

                    for related_model in related_models:
                        if related_model:
                            field = keywords[data_type]
                            value = getattr(related_model, field)
                            if isinstance(value,model_data):
                                data_temp += value.__str__()
                            else:
                                data_temp += value
            print()
            print(data_temp)
            print()
            if not data_temp: data_temp = 'Not Available'
            data.append(data_temp)
        profiles_temp.append({'profile':profile,'data':data})
    profiles = profiles_temp

    print()
    print(profiles)
    print()



    # # Loop through every profile
    # profiles_temp = []
    # for profile in profiles:
    #     # Get requested data for profile
    #     data = []
    #     for data_type in data_displayed: # Loop through requested data
    #         data_temp = None
    #         if data_type: # if data is requested
    #             # If data requested is part of the residence model
    #             if (data_type in residence_data):
    #                 # Get the current residence model
    #                 residence = profile.order_residences().first()
    #                 # If one was found get the data
    #                 if residence:
    #                     data_temp = getattr(residence,keywords[data_type])
    #             # If data requested is part of children model
    #             elif (data_type == 'children'):
    #                 children = profile.order_children() # Get children
    #                 data_temp = ''
    #                 i = 0
    #                 for child in children:
    #                     i += 1
    #                     if i == len(children): data_temp += child.first_name
    #                     else: data_temp += child.first_name + ', '
    #             # If data requested is part of role model
    #             elif (data_type in role_data):
    #                 if (data_type[0:7] == 'current'): roles = profile.roles.filter(end_date=None)
    #                 else: roles = profile.roles.all()
    #                 data_temp = ''
    #                 i = 0
    #                 for role in roles:
    #                     i += 1
    #                     temp = getattr(role,keywords[data_type])
    #                     if i == len(roles): # For last item
    #                         if temp: # If value found
    #                             data_temp += temp
    #                         else: # If value not found
    #                             data_temp = data_temp[:-2] # Remove comma from last item
    #                     else:
    #                         if temp: data_temp += temp + ', '  #BUGBUGBUGBUG
    #             # If data requested is part of training model
    #             elif (data_type in training_data):
    #                 training = profile.training.exclude(end_date=None)
    #                 data_temp = ''
    #                 for item in training:
    #                     data_temp += item.subject + ' '
    #             # If data is part of main profile model
    #             else:
    #                 data_temp = getattr(profile,data_type)
    #              # If data is a phone number
    #             if data_temp and ((data_type == 'cell') or (data_type == 'e_phone')):
    #                 data_temp = data_temp.as_e164 # Turn into a string
    #             if not data_temp: # if the field is empty return not available
    #                 data_temp = 'not available'
    #             data.append(data_temp) # Add that data result to list of data
    #     profiles_temp.append({'profile':profile,'data':data})
    # profiles = profiles_temp
    return profiles


def sort_profiles(profiles, sort_by):
    sorted_profiles = []
    for profile_object in profiles:
        group_names = []
        profile = profile_object['profile']
        if sort_by == '':
            group_names = ['no groups'] # User doesn't want them sorted
        elif (sort_by in residence_data): # If sort data is in residence model
            # Get the current residence model
            residence = profile.order_residences().first()
            # If one was found get the data
            if residence:
                group_names = [getattr(residence,keywords[sort_by])]
            else:
                group_names = [None]
        elif (sort_by in role_data): # If sort data is in role model
            current_roles = profile.roles.filter(end_date=None) # Get current roles
            for role in current_roles: # Add the roles to the profile's group names
                name = getattr(role,keywords[sort_by])
                if name: group_names.append(name)
            # IF the profile has no current roles
            if len(group_names) == 0: group_names = [None]
        else:
            group_names = [getattr(profile,sort_by)] # Get the requested sort attribute
        # Make sure group_names is a list of strings
        i = 0
        for group_name in group_names:
            if isinstance(group_name, model_data):
                group_names[i] = group_name.__str__()
            if not group_name:
                # Profile has no data for this field
                group_names[i] = 'Not Assigned'
            i += 1
        # Loop through list of groups (a group is a dictionary)
        profile_added = False
        for group in sorted_profiles:
            for group_name in group_names:
                if group_name == group['group name']: # Same group
                    group['profiles'].append(
                        {
                            'first name' : profile.first_name,
                            'last name' : profile.last_name,
                            'pk' : profile.pk,
                            'data' : profile_object['data']
                        }
                    ) # Add the profile to this group
                    profile_added = True
        if not profile_added: # No other group member in list yet.  Make
            # new group(s)
            for group_name in group_names:
                sorted_profiles.append(
                    {
                        'group name': group_name,
                        'profiles': [
                            {
                                'first name' : profile.first_name,
                                'last name' : profile.last_name,
                                'pk' : profile.pk,
                                'data' : profile_object['data']
                            }
                        ]
                    }
                )
    return sorted_profiles

# Get the choices of a certain field
def get_field_options(filterby):
    options = []
    if filterby in residence_data:
        field = Residence._meta.get_field(keywords[filterby])
    elif filterby in role_data:
        field = Role._meta.get_field(keywords[filterby])
    elif filterby in training_data:
        field = Training._meta.get_field(keywords[filterby])
    else:
        field = Profile._meta.get_field(filterby)
    # IF the field is a related model, get all the objects
    if field.get_internal_type() == 'ForeignKey':
        temp_options = field.remote_field.model.objects.all()
        # Add the names of the objects to the options
        for option in temp_options:
            options.append(option.__str__())
    # For a regular field type
    else:
        temp_options = field.choices
        # Places the readable option into a list
        for option in temp_options:
            options.append(option[1])

    return options

def create_excel(request, sorted_profiles):
    output = BytesIO()
    # Feed a buffer to workbook
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("profiles")
    bold = workbook.add_format({'bold': True})
    light = workbook.add_format()

    # Fill out the datasheet

    fields = request.GET.get('data_displayed')
    fields = json.loads(fields)
    row = 0
    if fields[0]:
        # Fill first row with field description
        for i, field in enumerate(fields):
            worksheet.write(row, i+1, display_text[field], bold)

        row += 1 # move down a row


    # Add profiles and their data
    for group in sorted_profiles["groups"]:
        if not group["group name"] == "no groups":
            worksheet.write(row,0,group["group name"], bold)
            row += 1 # move down a row
        for i, profile in enumerate(group["profiles"]):
            worksheet.write(row, 0, profile["first name"] + " " + profile["last name"], bold)
            for j, data in enumerate(profile["data"]):
                worksheet.write(row, j+1, data, light)
            row += 1 # move down a row
        row += 1 # skip a row after each group
    workbook.close()
    output.seek(0)
    return output
