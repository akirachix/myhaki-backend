from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import CaseAssignmentViewSet, CaseViewSet,CPDPointViewSet


router = DefaultRouter()
router.register(r'cases', CaseViewSet)
router.register(r'cpd-points', CPDPointViewSet, basename='cpdpoint')
router.register(r'case-assignments', CaseAssignmentViewSet, basename='case-assignment')


urlpatterns = [
   path('', include(router.urls)),
]
