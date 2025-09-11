

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from api.serializers import CaseSerializer
from .models import Case, CaseAssignment
from users.models import LawyerProfile

User = get_user_model()

class CaseAssignmentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='my-cases')
    def my_cases(self, request):
        try:
            lawyer_profile = request.user.lawyer_profile
        except LawyerProfile.DoesNotExist:
            return Response({"error": "You are not a lawyer"}, status=403)

        assignments = CaseAssignment.objects.filter(lawyer=lawyer_profile, is_assigned=True)
        cases = [assignment.case for assignment in assignments]
        serializer = CaseSerializer(cases, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='all-assignments')
    def all_assignments(self, request):
        if request.user.role != 'lsk_admin':
            return Response({"error": "Access denied"}, status=403)

        assignments = CaseAssignment.objects.filter(is_assigned=True).select_related(
            'case', 'case__detainee', 'lawyer', 'lawyer__user'
        )
        
        result = []
        for assignment in assignments:
            case_data = CaseSerializer(assignment.case).data
            lawyer_data = {
                'lawyer_name': f"{assignment.lawyer.user.first_name} {assignment.lawyer.user.last_name}",
                'practice_number': assignment.lawyer.practice_number,
                'email': assignment.lawyer.user.email
            }
            result.append({
                'assignment_id': assignment.assignment_id,
                'case': case_data,
                'assigned_lawyer': lawyer_data,
                'assign_date': assignment.assign_date
            })
        
        return Response(result)

    @action(detail=True, methods=['get'], url_path='my-lawyer')
    def my_lawyer(self, request, pk=None):
        case = get_object_or_404(Case, pk=pk)
        assignment = CaseAssignment.objects.filter(case=case, is_assigned=True).first()
        if not assignment:
            return Response({"error": "No lawyer assigned yet"}, status=404)

        lawyer_data = {
            'name': f"{assignment.lawyer.user.first_name} {assignment.lawyer.user.last_name}",
            'practice_number': assignment.lawyer.practice_number,
            'email': assignment.lawyer.user.email,
            'phone': assignment.lawyer.user.phone_number or "Not provided"
        }
        return Response(lawyer_data)