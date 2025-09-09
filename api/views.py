from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from cases.models import CaseAssignment
from .serializers import CaseAssignmentSerializer
from rest_framework.response import Response
from cpd.models import CPDPoint
from .serializers import CPDPointSerializer
from cases.models import CaseAssignment, Case
from .serializers import CaseAssignmentSerializer, CaseSerializer



class CaseAssignmentViewSet(viewsets.ModelViewSet):
   queryset = CaseAssignment.objects.all()
   serializer_class = CaseAssignmentSerializer
   permission_classes = [AllowAny]  

class CPDPointViewSet(viewsets.ModelViewSet):
    queryset = CPDPoint.objects.all()
    serializer_class = CPDPointSerializer

class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  
