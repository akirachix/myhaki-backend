from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
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
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True) 
        self.perform_update(serializer)
        return Response(serializer.data)

