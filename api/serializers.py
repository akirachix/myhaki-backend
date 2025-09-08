from rest_framework import serializers
from cases.models import Case, CaseAssignment, Detainee


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


class CaseAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseAssignment
        fields = '__all__'


class DetaineeSerializer(serializers.ModelSerializer):
   class Meta:
       model = Detainee
       fields = '__all__'