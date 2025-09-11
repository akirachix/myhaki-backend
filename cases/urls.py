# case/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import CaseAssignmentViewSet

router = DefaultRouter()
router.register(r'assignments', CaseAssignmentViewSet, basename='case-assignment')

urlpatterns = [
    path('', include(router.urls)),
]