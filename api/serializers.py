from rest_framework import serializers
from cases.models import CaseAssignment,Detainee, Case

class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = '__all__'

class CaseAssignmentSerializer(serializers.ModelSerializer):
   class Meta:
       model = CaseAssignment
       fields = '__all__'

class DetaineeSerializer(serializers.ModelSerializer):
   class Meta:
       model = Detainee
       fields = '__all__'
