from rest_framework import viewsets
from rest_framework.permissions import  IsAuthenticated, AllowAny
from django.shortcuts import render
from cases.models import CaseAssignment,Detainee
from .serializers import CaseAssignmentSerializer,DetaineeSerializer



class CaseAssignmentViewSet(viewsets.ModelViewSet):
   queryset = CaseAssignment.objects.all()
   serializer_class = CaseAssignmentSerializer
   permission_classes = [AllowAny]  


class DetaineeViewSet(viewsets.ModelViewSet):
   queryset = Detainee.objects.all()
   serializer_class = DetaineeSerializer
   permission_classes = [AllowAny]  
