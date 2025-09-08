from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from cases.models import CaseAssignment
from .serializers import CaseAssignmentSerializer
from rest_framework.response import Response
from cpd.models import CPDPoint
from .serializers import CPDPointSerializer

class CaseAssignmentViewSet(viewsets.ModelViewSet):
   queryset = CaseAssignment.objects.all()
   serializer_class = CaseAssignmentSerializer
   permission_classes = [AllowAny]  


class CPDPointViewSet(viewsets.ModelViewSet):
    queryset = CPDPoint.objects.all()
    serializer_class = CPDPointSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"message": "CPD Points API", "data": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"message": "CPD Point Details", "data": serializer.data})