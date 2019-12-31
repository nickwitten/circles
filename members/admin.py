from django.contrib import admin
from .models import Profile, Site, Residence, Role, Child, ChildInfo, FilterSet

# Register your models here.

admin.site.register(Profile)
admin.site.register(Site)
admin.site.register(Residence)
admin.site.register(Role)
admin.site.register(Child)
admin.site.register(ChildInfo)
admin.site.register(FilterSet)
