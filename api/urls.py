from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import CaseAssignmentViewSet
from api.views import CPDPointViewSet


router = DefaultRouter()
router.register(r'cpd-points', CPDPointViewSet, basename='cpdpoint')
router.register(r'cases', CaseAssignmentViewSet, basename='cases')


urlpatterns = [
   path('', include(router.urls)),
]
