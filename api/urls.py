from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import CaseAssignmentViewSet, CaseViewSet,CPDPointViewSet,DetaineeViewSet, LawyerRegistrationView, ForgotPasswordView, VerifyCodeView, ResetPasswordView,UsersViewSet, UserSignupView, LoginView,MyCaseViewSet
from rest_framework.authtoken.views import obtain_auth_token


router = DefaultRouter()
router.register(r'cases', CaseViewSet)
router.register(r'cpd-points', CPDPointViewSet, basename='cpdpoint')
router.register(r'case-assignments', CaseAssignmentViewSet, basename='case-assignment')
router.register(r"users", UsersViewSet, basename="users")
router.register(r"detainees", DetaineeViewSet, basename="detainees")
router.register(r"my-cases", MyCaseViewSet, basename="my-cases")
# router.register(r"my-cases", MyCaseViewSet, basename="my-cases")



urlpatterns = [
   path('', include(router.urls)),
   path('register-lawyer/', LawyerRegistrationView.as_view(), name='register-lawyer'),
   path('forgotpassword/', ForgotPasswordView.as_view(), name='forgot-password'),
   path('verifycode/', VerifyCodeView.as_view(), name='verify-code'),
   path('resetpassword/', ResetPasswordView.as_view(), name='reset-password'),
   path('login/', LoginView.as_view(), name='api_token_auth'),
   path('signup/', UserSignupView.as_view(), name='api_signup'),
]


