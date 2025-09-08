
from rest_framework import serializers
from cases.models import CaseAssignment

class CaseAssignmentSerializer(serializers.ModelSerializer):
   class Meta:
       model = CaseAssignment
       fields = '__all__'