from rest_framework import viewsets
from rest_framework.permissions import  IsAuthenticated, AllowAny
from django.shortcuts import render
from cases.models import CaseAssignment,Detainee, Case
from .serializers import CaseAssignmentSerializer,DetaineeSerializer, CaseSerializer


class CaseAssignmentViewSet(viewsets.ModelViewSet):
   queryset = CaseAssignment.objects.all()
   serializer_class = CaseAssignmentSerializer
   permission_classes = [AllowAny]  
class DetaineeViewSet(viewsets.ModelViewSet):
   queryset = Detainee.objects.all()
   serializer_class = DetaineeSerializer
   permission_classes = [AllowAny]  
class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  

