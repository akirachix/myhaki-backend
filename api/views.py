from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from cases.models import CaseAssignment
from .serializers import CaseAssignmentSerializer



class CaseAssignmentViewSet(viewsets.ModelViewSet):
   queryset = CaseAssignment.objects.all()
   serializer_class = CaseAssignmentSerializer
   permission_classes = [AllowAny]  





