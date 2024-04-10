# your_app/admin.py

from .models import Remark
from django.contrib import admin
from .models import Case


class CaseAdmin(admin.ModelAdmin):
    list_display = ('id','case_number', 'missing_person',
                    'status',  'found_person', 'type')
    search_fields = ('case_number', 'missing_person__first_name',
                     'missing_person__last_name')


admin.site.register(Case, CaseAdmin)


class RemarksAdmin(admin.ModelAdmin):
    list_display = ['case_id', 'remarks', 'created_at', 'created_by']

admin.site.register(Remark, RemarksAdmin)
