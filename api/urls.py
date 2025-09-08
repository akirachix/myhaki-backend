from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import CaseAssignmentViewSet,DetaineeViewSet


router = DefaultRouter()
router.register(r'case-assignments', CaseAssignmentViewSet, basename='case-assignments')
router.register(r'detainees', DetaineeViewSet, basename='detainees') 



urlpatterns = [
   path('', include(router.urls)),
]



