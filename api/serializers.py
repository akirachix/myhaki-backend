from rest_framework import serializers 
from cases.models import Detainee

class DetaineeSerializer(serializers.ModelSerializer):
   class Meta:
       model = Detainee
       fields = '__all__'
