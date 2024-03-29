from django.db.models.functions import Concat
from django.db.models import Value
from phonenumber_field.phonenumber import PhoneNumber
from .models import Profile, Site, Residence, Role, Child
from learning.models import ProfileModule, ProfileTheme, Module, Theme
import json
from io import BytesIO
import xlsxwriter

######### Fill for new fields and models #########

# All data values that are models
model_data = (Site, Child, Module, Theme)

# HTML Value --> (Model Field Name, HTML Display)

profile_data = {
    'email': ('email_address', 'Email'),
    'cell': ('cell_phone', 'Cell'),
    'circles_id': ('circles_ID', 'ID'),
    'status': ('status', 'Status'),
    'birthdate': ('DOB', 'Birthdate'),
    'race': ('race', 'Race'),
    'gender': ('gender', 'Gender'),
    'e_phone': ('e_phone', 'Emergency Number'),
}
residence_data = {
    'first_city': ('city', 'City'),
    'first_state': ('state', 'State'),
    'first_zip': ('zip', 'Zip'),
    'first_street_address': ('street_address', 'Address'),
    'first_home_ownership': ('ownership', 'Home Ownership'),
    'first_habitat_home': ('habitat', 'Habitat Home'),
    'first_safe_home': ('safety', 'Safe Home'),
    'first_repair_home': ('repair', 'Repair Home'),
}
role_data = {
    'current_site': ('site', 'Site'),
    'current_role': ('position', 'Current Role'),
    'all_roles': ('position', 'All Roles'),
    'current_cohort': ('cohort', 'Cohort'),
    'current_resource_team': ('resource_team_name', 'Resource Team'),
    'current_resource_team_role': ('resource_team_role', 'Resource Team Role'),
}
module_data = {
    'excurrent_module': ('module', 'Completed Modules'),  # completed modules
    'current_module': ('module', 'Incomplete Required Modules'),  # incomplete modules
}
theme_data = {
    'excurrent_theme': ('theme', 'Completed Theme'),  # completed themes
    'current_theme': ('theme', 'Incomplete Required Themes'),  # incomplete themes
}
child_data = {
    'all_children': ('first_name', 'Children'),
}
field_names = {}
for data in [profile_data, residence_data, role_data, module_data, theme_data, child_data]:
    field_names.update(data)

form_choices_text = [[key, value[1]] for key, value in sorted(field_names.items(), key=lambda x: x[1][1])]
form_choices_text.insert(0, ["",""])
site_spec_fields = list(module_data.keys()) + list(theme_data.keys())

########## Main Functions #########################


def get_profiles(tool_inputs, user):
    # #search_input = request.GET.get('search_input',None)
    # sort_by = request.GET.get('sort_by',None)
    # data_displayed = request.GET.get('data_displayed',None)
    # data_displayed = json.loads(data_displayed)
    # filters = request.GET.get('filters',None)
    # filters = json.loads(filters)
    try:
        data_type = json.loads(tool_inputs['datatype'])
    except Exception as e:
        print(type(e), e)
    try:
        filters = json.loads(tool_inputs['filters'])
    except Exception as e:
        print(type(e), e)
    profiles = user.userinfo.user_profile_access().order_by('last_name')
    profiles = search_profiles(profiles, tool_inputs['searchinput'] or '')
    profiles = filter_profiles(profiles, filters)
    profiles = get_profile_data(profiles, data_type)
    sorted_profiles = sort_profiles(profiles, tool_inputs['sortby'] or '')

    data = {
        'groups': sorted_profiles
    }
    return data


def search_profiles(profiles,search_input):
    search = {}
    # Anotate each profile with 'firstname lastname'
    annotated_queryset = profiles.annotate(fullname=Concat('first_name', Value(' '), 'last_name'))
    # Filter out elements that don't contain search input
    profiles = annotated_queryset.filter(fullname__icontains=search_input)
    return profiles


def filter_profiles(profiles,filters):
    for filter_ in filters:
        filterby = filter_["filterby"]
        filterinput = filter_["filterinput"]
        if not filterinput: # If there is no input don't filter_
            continue
        # Get model that the field is in
        model = field_to_model(filterby)
        # Get the field from the model
        field = model._meta.get_field(field_names[filterby][0])
        # If the field is a related model change search type
        if field.get_internal_type() == 'ForeignKey':
            # search_type = '__' + field_names[filterby][0]
            search_type = '__pk'
        else:
            search_type = '__icontains'
        # When the field is in the top Profile model
        if model == Profile:
            query = {}
            query[field_names[filterby][0] + search_type] = filterinput
            profiles = profiles.filter(**query)
        # When the field is in a related model
        else:
            # Build query
            query = {}
            if filterby[0:7] == 'current':
                query['end_date'] = None
            query[field_names[filterby][0] + search_type] = filterinput
            # All profiles who have an object that passes query in this List
            profile_ids = []
            for profile in profiles:
                related_models = model.get_related(profile)
                if 'excurrent' in filterby:
                    related_models = related_models.exclude(end_date=None)
                if 'not' in filterby and not related_models.filter(**query):
                    profile_ids.append(profile.pk)
                elif 'not' not in filterby and related_models.filter(**query):
                    profile_ids.append(profile.pk)
            # Query profiles with pk in profile_ids
            profiles = profiles.filter(pk__in=profile_ids)

    return profiles

def get_profile_data(profiles, data_types):
    profiles_temp = []
    for profile in profiles:
        data = []
        for data_type in data_types:
            data_temp = ''
            if data_type:
                model = field_to_model(data_type)
                if model == Profile:
                    value = getattr(profile,field_names[data_type][0])
                    data_temp += data_to_string(value)
                else:
                    related_models = model.get_related(profile)
                    # Different Queries on Related Models
                    related_models = query_related(related_models, data_type)
                    for index, related_model in enumerate(related_models):
                        if related_model:
                            field = field_names[data_type][0]
                            value = getattr(related_model, field)
                            data_temp += data_to_string(value)
                            if index < len(related_models) - 1:
                                data_temp += ', '
                if not data_temp:
                    data_temp = 'Not Available'
            data.append(data_temp)
        profiles_temp.append({'profile':profile,'data':data})
    profiles = profiles_temp

    return profiles


def sort_profiles(profiles, sort_by):
    sorted_profiles = []
    for profile_object in profiles:
        group_names = []
        profile = profile_object['profile']
        if sort_by == '':
            group_names = ['no groups']
        else:
            model = field_to_model(sort_by)
            if model == Profile:
                value = getattr(profile,field_names[sort_by][0])
                if value:
                    name = data_to_string(value)
                    group_names.append(name)
            else:
                related_models = model.get_related(profile)
                related_models = query_related(related_models, sort_by)
                for model in related_models:
                    if model:
                        value = getattr(model, field_names[sort_by][0])
                        if value:
                            name = data_to_string(value)
                            group_names.append(name)
            if len(group_names) == 0:
                group_names = [None]
            for i, group_name in enumerate(group_names):
                if not group_name: group_names[i] = 'Not Available'
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
    model = field_to_model(filterby)
    field = model._meta.get_field(field_names[filterby][0])
    # IF the field is a related model, get all the objects
    if field.get_internal_type() == 'ForeignKey':
        temp_options = field.remote_field.model.objects.all()
        # Add the names of the objects to the options
        for option in temp_options:
            option_str = option.__str__()
            if filterby in site_spec_fields:
                option_str = '{} - {}'.format(option.site, option_str)
            options.append([option_str, option.pk])
    # For a regular field type
    else:
        temp_options = field.choices
        # Places the readable option into a list
        for option in temp_options:
            options.append([option[1], option[1]])
    return options

def create_excel(tools_form, sorted_profiles):
    output = BytesIO()
    # Feed a buffer to workbook
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("profiles")
    bold = workbook.add_format({'bold': True})
    light = workbook.add_format()

    # Fill out the datasheet

    fields = tools_form['datatype']
    fields = json.loads(fields)
    row = 0
    if fields[0]:
        # Fill first row with field description
        for i, field in enumerate(fields):
            worksheet.write(row, i+1, field_names[field][1], bold)

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
        row += 1  # skip a row after each group
    workbook.close()
    output.seek(0)
    return output


########## Helper Functions #######################


def field_to_model(field):
    if field in residence_data:
        return Residence
    elif field in role_data:
        return Role
    elif field in module_data:
        return ProfileModule
    elif field in theme_data:
        return ProfileTheme
    elif field in child_data:
        return Child
    else:
        return Profile



def data_to_string(value):
    if value is None:
        return ''  # This will be 'Not Available'
    elif isinstance(value,PhoneNumber):
        return value.as_e164
    else:
        return str(value)


def query_related(related_models, data_type):
    if 'first' in data_type: related_models = [related_models.first()]
    elif 'all' in data_type: related_models = list(related_models)
    elif 'excurrent' in data_type: related_models = list(related_models.exclude(end_date=None))
    elif 'current' in data_type: related_models = list(related_models.filter(end_date=None))
    return related_models


def unique_maintain_order(x):
    seen = list()
    seen_add = seen.append
    z = [y for y in x if not (y in seen or seen_add(y))]
    return z

