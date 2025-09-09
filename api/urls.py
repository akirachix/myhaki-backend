from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import CaseAssignmentViewSet,DetaineeViewSet,CaseViewSet

router = DefaultRouter()
router.register(r'cases', CaseViewSet)
router.register(r'cases-assignments', CaseAssignmentViewSet, basename='case-assignments')
router.register(r'detainees', DetaineeViewSet, basename='detainees') 

urlpatterns = [
   path('', include(router.urls)),
]



