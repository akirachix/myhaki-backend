from rest_framework import serializers
from cpd.models import CPDPoint

class CPDPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPDPoint
        fields = '__all__'