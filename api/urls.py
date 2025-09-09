from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import CaseAssignmentViewSet, CaseViewSet,CPDPointViewSet,DetaineeViewSet


router = DefaultRouter()
router.register(r'cases', CaseViewSet)
router.register(r'cpd-points', CPDPointViewSet, basename='cpdpoint')
router.register(r'case-assignments', CaseAssignmentViewSet, basename='case-assignment')
router.register(r'detainees', DetaineeViewSet, basename='detainees') 

urlpatterns = [
   path('', include(router.urls)),
]
