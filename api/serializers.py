from rest_framework import serializers
from cases.models import Case, CaseAssignment

class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = '__all__'


class CaseAssignmentSerializer(serializers.ModelSerializer):
   class Meta:
       model = CaseAssignment
       fields = '__all__'
