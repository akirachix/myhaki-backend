from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import CaseAssignmentViewSet


router = DefaultRouter()
router.register(r'cases', CaseAssignmentViewSet, basename='cases')



urlpatterns = [
   path('', include(router.urls)),
]



