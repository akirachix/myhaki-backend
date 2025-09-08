
from rest_framework import serializers
from cases.models import CaseAssignment,Detainee

class CaseAssignmentSerializer(serializers.ModelSerializer):
   class Meta:
       model = CaseAssignment
       fields = '__all__'


class DetaineeSerializer(serializers.ModelSerializer):
   class Meta:
       model = Detainee
       fields = '__all__'
