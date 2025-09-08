from rest_framework import serializers
from cpd.models import CPDPoint
from cases.models import CaseAssignment

class CPDPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPDPoint
        fields = '__all__'

class CaseAssignmentSerializer(serializers.ModelSerializer):
   class Meta:
       model = CaseAssignment
       fields = '__all__'
