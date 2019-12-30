from django.db.models.functions import Concat
from django.db.models import Value

# Types of data that need to be fetched from a residence model
residence_data = ['street_address','city','state','zip','home_ownership','habitat_home','safe_home','repair_home']
# Types of data that need to be fetched from a role model
role_data = ['current_site','current_role','all_roles','current_cohort','current_resource_team','current_resource_team_role']
# Types of data that need to be fetched from a training model
training_data = ['completed_training','incomplete_training']

keywords = {
    'current_site':'site',
    'city':'city',
    'state':'state',
    'zip':'zip',
    'street_address':'street_address',
    'current_role':'position',
    'all_roles':'position',
    'current_cohort':'cohort',
    'current_resource_team':'resource_team_name',
    'current_resource_team_role':'resource_team_role',
    'completed_training':'subject',
    'incomplete_training':'subject',
    'home_ownership':'ownership',
    'habitat_home':'habitat',
    'safe_home':'safe',
    'repair_home':'repair',
}


def search_profiles(profiles,search_input):
    search = {}
    # Anotate each profile with 'firstname lastname'
    annotated_queryset = profiles.annotate(fullname = Concat('first_name', Value(' '), 'last_name'))
    # Filter out elements that don't contain search input
    profiles = annotated_queryset.filter(fullname__icontains=search_input)
    return profiles


def filter_profiles(profiles,filters):

    # Saved filters (filters that have been added)
    # List of [(filterby, filterinput)]
    for filter in filters:
        filterby = filter["filterby"]
        filterinput = filter["filterinput"]
        if not filterinput: # If there is no input don't filter
            continue

        # For data that needs to be retrieved from a related model
        elif filterby in residence_data or filterby in role_data or filterby in training_data:
            profile_ids = []
            for profile in profiles:
                # For residence model
                if filterby in residence_data:
                    # Set query fields
                    query = {'end_date':None, keywords[filterby]+'__icontains':filterinput}
                    # If found add profile
                    if profile.order_residences().filter(**query):
                        profile_ids.append(profile.pk)
                # For role model
                elif filterby in role_data:
                    # Set query fields
                    if (filterby[0:7]=='current'): query = {'end_date':None, keywords[filterby]+'__icontains':filterinput}
                    else: query = {keywords[filterby]+'__icontains':filterinput}
                    # If found add profile
                    if profile.order_roles().filter(**query):
                        profile_ids.append(profile.pk)
                # For training model
                elif filterby in training_data:
                    # Get a list of all completed trainings
                    completed_trainings = profile.training.exclude(date_completed=None)
                    # Set query
                    query = {keywords[filterby]+'__icontains':filterinput}
                    # Check if profile has the completed training in filterinput
                    if (filterby=='completed_training' and completed_trainings.filter(**query)):
                        profile_ids.append(profile.pk)
                    # Check if the profile doesnt have the completed training
                    if (filterby=='incomplete_training' and not completed_trainings.filter(**query)):
                        profile_ids.append(profile.pk)

            profiles = profiles.filter(pk__in=profile_ids) # Query all found profiles


        # Data is in the profile model
        else:
            query = {}
            query[filter["filterby"] + '__icontains'] = filter["filterinput"]
            profiles = profiles.filter(**query)

    return profiles

def get_profile_data(profiles, data_displayed):
    # Loop through every profile
    profiles_temp = []
    for profile in profiles:
        # Get requested data for profile
        data = []
        for data_type in data_displayed: # Loop through requested data
            data_temp = None
            if data_type: # if data is requested
                # If data requested is part of the residence model
                if (data_type in residence_data):
                    # Get the current residence model
                    residence = profile.order_residences().first()
                    # If one was found get the data
                    if residence:
                        data_temp = getattr(residence,keywords[data_type])
                # If data requested is part of children model
                elif (data_type == 'children'):
                    children = profile.order_children() # Get children
                    data_temp = ''
                    for child in children:
                        data_temp += child.first_name + ' '
                # If data requested is part of role model
                elif (data_type in role_data):
                    if (data_type[0:7] == 'current'): roles = profile.roles.filter(end_date=None)
                    else: roles = profile.roles.all()
                    data_temp = ''
                    for role in roles:
                        temp = getattr(role,keywords[data_type])
                        if temp:
                            data_temp += temp + ' '
                # If data requested is part of training model
                elif (data_type in training_data):
                    training = profile.training.exclude(date_completed=None)
                    data_temp = ''
                    for item in training:
                        data_temp += item.subject + ' '
                # If data is part of main profile model
                else:
                    data_temp = getattr(profile,data_type)
                 # If data is a phone number
                if data_temp and ((data_type == 'cell') or (data_type == 'e_phone')):
                    data_temp = data_temp.as_e164 # Turn into a string
                if not data_temp: # if the field is empty return not available
                    data_temp = 'not available'
                data.append(data_temp) # Add that data result to list of data
        profiles_temp.append({'profile':profile,'data':data})
    profiles = profiles_temp
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
        i = 0
        for group_name in group_names:
            if group_name == None:
                # Profile has no data for this field
                group_names[i] = 'Not Assigned'
            ++i
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
