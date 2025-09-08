from rest_framework import viewsets 
from rest_framework.permissions import IsAuthenticated, AllowAny 
from cases.models import Detainee
from .serializers import DetaineeSerializer


class DetaineeViewSet(viewsets.ModelViewSet):
   queryset = Detainee.objects.all()
   serializer_class = DetaineeSerializer
   permission_classes = [AllowAny]  
