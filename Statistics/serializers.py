from .models import Remark
from rest_framework import serializers
from .models import Case


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ['id','case_number', 'missing_person', 'status', 'found_person','type','created_at']


class RemarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remark
        fields = ['id', 'case_id', 'remarks', 'created_at', 'created_by']
