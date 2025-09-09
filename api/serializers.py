from rest_framework import serializers
from cpd.models import CPDPoint
from cases.models import CaseAssignment,Detainee, Case

class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = '__all__'

    def validate(self, data):
        if data.get('monthly_income') == 'greater_than_30000':
            raise serializers.ValidationError(
                {"monthly_income": "You are not eligible for this service due to income above 30000."}
            )
        return data

class CPDPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPDPoint
        fields = '__all__'

class CaseAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseAssignment
        fields = '__all__'


class DetaineeSerializer(serializers.ModelSerializer):
   class Meta:
       model = Detainee
       fields = '__all__'