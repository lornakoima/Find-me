
from .models import MissingPerson, MissingPersonLocation, FoundPerson, FoundPersonLocation
from django.contrib.auth.models import Group

from django.contrib import admin


@admin.register(FoundPerson)
class FoundPersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'age', 'created_at')
    search_fields = ('first_name', 'last_name', 'description')


@admin.register(FoundPersonLocation)
class FoundPersonLocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'county', 'name', 'time_found')
    search_fields = ('county', 'name')


@admin.register(MissingPerson)
class MissingPersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name',
                    'age', 'created_at', 'created_by')
    search_fields = ('first_name', 'last_name', 'description')


@admin.register(MissingPersonLocation)
class MissingPersonLocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'latitude', 'longitude',
                    'missing_person', 'county', 'name', 'time_seen')
    search_fields = ('county', 'name')


admin.site.unregister(Group)
