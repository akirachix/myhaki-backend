from rest_framework import viewsets
from rest_framework.permissions import  IsAuthenticated, AllowAny
from django.shortcuts import render
from rest_framework.response import Response
from .serializers import CaseAssignmentSerializer, CaseSerializer,CPDPointSerializer,DetaineeSerializer
from cases.models import CaseAssignment,Detainee, Case
from cpd.models import CPDPoint

class CaseAssignmentViewSet(viewsets.ModelViewSet):
   queryset = CaseAssignment.objects.all()
   serializer_class = CaseAssignmentSerializer
   permission_classes = [AllowAny]  

class CPDPointViewSet(viewsets.ModelViewSet):
    queryset = CPDPoint.objects.all()
    serializer_class = CPDPointSerializer

class DetaineeViewSet(viewsets.ModelViewSet):
   queryset = Detainee.objects.all()
   serializer_class = DetaineeSerializer
   permission_classes = [AllowAny]  

class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  
