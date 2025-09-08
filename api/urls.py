from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import CPDPointViewSet


router = DefaultRouter()
router.register(r'cpd-points', CPDPointViewSet, basename='cpdpoint')

urlpatterns = [
    path('', include(router.urls)),  
]