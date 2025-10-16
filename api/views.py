from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from rest_framework import viewsets, status,permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import CaseAssignmentSerializer, CaseSerializer,CPDPointSerializer,DetaineeSerializer
from .serializers import CaseAssignmentSerializer, CaseSerializer,CPDPointSerializer,DetaineeSerializer, LawyerRegistrationSerializer,ForgotPasswordSerializer,VerifyCodeSerializer,ResetPasswordSerializer,ApplicantSerializer, UserSerializer, LawyerProfileSerializer
from cases.models import CaseAssignment,Detainee, Case
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .serializers import CaseSerializer, CaseAssignmentSerializer, CPDPointSerializer, DetaineeSerializer, LawyerRegistrationSerializer, ForgotPasswordSerializer, VerifyCodeSerializer, ResetPasswordSerializer, UserSerializer, LawyerProfileSerializer
from cases.models import CaseAssignment, Detainee, Case
from cpd.models import CPDPoint
from django_filters.rest_framework import DjangoFilterBackend
from users.models import LawyerProfile, User
from rest_framework.views import APIView
from django.core.mail import send_mail
import random
from django.conf import settings
from rest_framework.views import APIView
from users.permissions import IsAdmin, IsUser
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from users.models import LawyerProfile  
from users.permissions import IsAdmin, IsUser
from .permissions import IsAdminOrReadOnly 
from cases.services import update_case_and_cpd, assign_case_automatically
from api.permissions import IsAdminOrReadOnly, IsAdminOrIsAssignedLawyer 
from api.serializers import CaseSerializer, CaseAssignmentSerializer 
from cases.models import Case, CaseAssignment
from users.models import LawyerProfile

User = get_user_model()

class PlaceholderAssignmentSerializer: pass 
try:
    serializer_class = CaseAssignmentSerializer
except NameError:
    serializer_class = PlaceholderAssignmentSerializer 

class CaseAssignmentViewSet(viewsets.ModelViewSet):
    queryset = CaseAssignment.objects.all()
    serializer_class = CaseAssignmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['case__status', 'status', 'lawyer']
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly] 

    def get_permissions(self):
        """
        Dynamically assigns permission classes based on the action requested.
        """
        if self.action in ['my_cases', 'all_assignments', 'my_lawyer']:
            return [IsAuthenticated()]
        
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrIsAssignedLawyer()]

        return [IsAuthenticated(), IsAdminOrReadOnly()]

    def get_queryset(self):
        """Restricts queryset based on user role."""
        user = self.request.user
        if user.role == 'lsk_admin':
            return CaseAssignment.objects.all().select_related('case', 'lawyer', 'lawyer__user')
        try:
            lawyer_profile = user.lawyer_profile
            return CaseAssignment.objects.filter(lawyer=lawyer_profile).select_related('case', 'lawyer', 'lawyer__user')
        except LawyerProfile.DoesNotExist:
            case_ids = Case.objects.filter(detainee__user=user).values_list('case_id', flat=True)
            return CaseAssignment.objects.filter(case__in=case_ids).select_related('case', 'lawyer', 'lawyer__user')


    @action(detail=True, methods=['post'], url_path='accept')
    def accept_case(self, request, pk=None):
        """Lawyer accepts a pending assigned case."""
        assignment = self.get_object()
        
        if assignment.lawyer.user != request.user:
             return Response({"detail": "Permission denied. You are not the assigned lawyer."}, status=status.HTTP_403_FORBIDDEN)
        
        if assignment.status != 'pending':
            return Response({"detail": f"Case already processed with status: {assignment.status}"}, status=status.HTTP_400_BAD_REQUEST)

        assignment.status = 'accepted'
        assignment.confirmed_by_lawyer = True
        assignment.save()

        case = assignment.case
        case.status = 'accepted'
        case.stage = 'in_progress'
        case.save()

        CaseAssignment.objects.filter(
            case=case, 
            status__in=['pending', 'reassigned']
        ).exclude(pk=assignment.pk).update(status='handled', reject_reason='Accepted by another lawyer.')

        return Response({"detail": "Case accepted. Status is now 'in_progress'."}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], url_path='reject')
    def reject_case(self, request, pk=None):
        """Lawyer rejects a pending assigned case."""
        assignment = self.get_object()
        
        if assignment.lawyer.user != request.user:
             return Response({"detail": "Permission denied. You are not the assigned lawyer."}, status=status.HTTP_403_FORBIDDEN)

        if assignment.status != 'pending':
            return Response({"detail": f"Case already processed with status: {assignment.status}"}, status=status.HTTP_400_BAD_REQUEST)

        assignment.status = 'rejected'
        assignment.reject_reason = request.data.get('reason', 'Lawyer explicitly rejected the case.')
        assignment.save()

        reassignment_result = assign_case_automatically(assignment.case.case_id)
        
        if reassignment_result and reassignment_result.get('status') == 'assignment_failed':
             return Response(reassignment_result.get('notice'), status=status.HTTP_200_OK)
        
        return Response({"detail": "Case rejected. New assignment triggered (if available)."}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], url_path='confirm-completion')
    def confirm_completion(self, request, pk=None):
        """Lawyer confirms they have completed the case work."""
        assignment = self.get_object()
        
        if assignment.lawyer.user != request.user:
             return Response({"detail": "Permission denied. You are not the assigned lawyer."}, status=status.HTTP_403_FORBIDDEN)
        
        if assignment.status != 'accepted':
            return Response({"detail": "Completion can only be confirmed on an accepted case."}, status=status.HTTP_400_BAD_REQUEST)

        assignment.confirmed_by_lawyer = True
        assignment.save()

        update_case_and_cpd(assignment) 
        
        return Response({"detail": "Lawyer completion confirmed. Awaiting applicant confirmation."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='applicant-confirm-completion')
    def applicant_confirm_completion(self, request, pk=None):
        """Applicant confirms the case work has been completed by the lawyer."""
        assignment = self.get_object()

        if assignment.case.detainee and assignment.case.detainee.user != request.user:
            return Response({"detail": "Permission denied. You are not the associated applicant."}, status=status.HTTP_403_FORBIDDEN)

        if assignment.status != 'accepted':
            return Response({"detail": "Completion can only be confirmed on an accepted case."}, status=status.HTTP_400_BAD_REQUEST)
        
        assignment.confirmed_by_applicant = True
        assignment.save()
        
        update_case_and_cpd(assignment) 

        return Response({"detail": "Applicant completion confirmed. Case status updated."}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['get'], url_path='my-cases')
    def my_cases(self, request):
        try:
            lawyer_profile = request.user.lawyer_profile
        except LawyerProfile.DoesNotExist:
            return Response({"error": "You are not a lawyer"}, status=status.HTTP_403_FORBIDDEN)

        assignments = CaseAssignment.objects.filter(lawyer=lawyer_profile, is_assigned=True)
        cases = [assignment.case for assignment in assignments]
        serializer = CaseSerializer(cases, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=['get'], url_path='all-assignments')
    def all_assignments(self, request):
        if request.user.role != 'admin':
            return Response({"error": "Access denied. Requires admin role."}, status=status.HTTP_403_FORBIDDEN)

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
            return Response({"error": "No lawyer assigned yet"}, status=status.HTTP_404_NOT_FOUND)

        lawyer_data = {
            'name': f"{assignment.lawyer.user.first_name} {assignment.lawyer.user.last_name}",
            'practice_number': assignment.lawyer.practice_number,
            'email': assignment.lawyer.user.email,
            'phone': assignment.lawyer.user.phone_number or "Not provided"
        }
        return Response(lawyer_data)

    
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

    permission_classes = [AllowAny]  

class ApplicantCaseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Case.objects.filter(user=self.request.user)
 
class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role']

class LawyersViewSet(viewsets.ModelViewSet):
    queryset = LawyerProfile.objects.all()
    serializer_class = LawyerProfileSerializer

class LskAdminViewSet(viewsets.ModelViewSet):
    queryset = LawyerProfile.objects.filter(user__role='lsk_admin')
    serializer_class = LawyerProfileSerializer


class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role='applicant')
    serializer_class = UserSerializer


class LawyerRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LawyerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Lawyer registered and verified successfully.',
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

otp_storage = {}

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        otp = str(random.randint(1000, 9999))
        cache.set(f'otp_{email}', otp, timeout=300)
        send_mail(
            'Your OTP for password reset',
            f'Your OTP is {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({"detail": "OTP sent to your email."})

class VerifyCodeView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        cached_otp = cache.get(f'otp_{email}')
        if cached_otp is None:
          return Response({"detail": "OTP has expired, please request a new one."}, status=status.HTTP_400_BAD_REQUEST)
        elif cached_otp != otp:
          return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        cache.delete(f'otp_{email}')

        return Response({"detail": "OTP verified."})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()
        cache.delete(f'otp_{email}')
        return Response({"detail": "Password reset successful."})


class SomeAdminView(APIView):
    permission_classes = [IsAdmin]


class SomeUserView(APIView):
    permission_classes = [IsUser]


class UserSignupView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": serializer.data,
            "message": "User created successfully"
        }, status=status.HTTP_201_CREATED)




User = get_user_model()


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        practice_number = request.data.get('practice_number')
        email = request.data.get('email') or request.data.get('username')
        password = request.data.get('password')
        if not password:
            return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if practice_number:
            try:
                lawyer_profile = LawyerProfile.objects.get(
                    practice_number__iexact=practice_number.strip()
                )
                user = lawyer_profile.user
                if user.role != 'lawyer':
                    user = None
            except LawyerProfile.DoesNotExist:
                user = None

            if user and not user.check_password(password):
                user = None

       
        elif email:
            user = authenticate(request, username=email, password=password)
            if user and user.role == 'lawyer':
                user = None

        else:
            return Response({
                'error': 'Either practice_number (for lawyers) or email/username (for applicants and lsk_admin) must be provided'
            }, status=status.HTTP_400_BAD_REQUEST)

    
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

     
        if user.role not in ['applicant', 'lawyer', 'lsk_admin']:
            return Response({'error': 'Unauthorized role'}, status=status.HTTP_403_FORBIDDEN)

     
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'id': user.id,
        })