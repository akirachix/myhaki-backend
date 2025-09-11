from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import CaseAssignmentSerializer, CaseSerializer,CPDPointSerializer,DetaineeSerializer
from .serializers import CaseAssignmentSerializer, CaseSerializer,CPDPointSerializer,DetaineeSerializer, LawyerRegistrationSerializer,ForgotPasswordSerializer,VerifyCodeSerializer,ResetPasswordSerializer,ApplicantSerializer, UserSerializer, LawyerProfileSerializer
from cases.models import CaseAssignment,Detainee, Case
from cpd.models import CPDPoint
from django_filters.rest_framework import DjangoFilterBackend
from users.models import LawyerProfile, ApplicantProfile, User, LskAdminProfile
from rest_framework.views import APIView
from django.core.mail import send_mail
import random
from django.conf import settings
from rest_framework.views import APIView
from users.permissions import IsAdmin, IsUser
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


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
    queryset = LskAdminProfile.objects.all()
    serializer_class = LawyerProfileSerializer  


class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = ApplicantProfile.objects.all()
    serializer_class = ApplicantSerializer

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

from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

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
