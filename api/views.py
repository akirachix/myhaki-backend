from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
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
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from users.permissions import IsAdmin, IsUser

class CaseAssignmentViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing CaseAssignment instances.
    Provides standard CRUD operations and custom actions.
    """
    queryset = CaseAssignment.objects.all()
    serializer_class = CaseAssignmentSerializer
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
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        otp = str(random.randint(1000, 9999))
        otp_storage[email] = otp

        send_mail(
            'Your OTP for password reset',
            f'Your OTP is {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({"detail": "OTP sent to your email."})


class VerifyCodeView(APIView):
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        if otp_storage.get(email) != otp:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "OTP verified."})


class ResetPasswordView(APIView):
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
        otp_storage.pop(email, None)
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


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email') or request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'email': user.email})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)