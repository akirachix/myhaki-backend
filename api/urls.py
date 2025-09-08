from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import CaseAssignmentViewSet, CaseViewSet

router = DefaultRouter()
router.register(r'cases', CaseViewSet)
router.register(r'cases-assignments', CaseAssignmentViewSet, basename='cases')

urlpatterns = [
   path('', include(router.urls)),
]



