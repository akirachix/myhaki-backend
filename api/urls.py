from django.urls import include, path
from rest_framework.routers import DefaultRouter 
from .views import DetaineeViewSet, DetaineeViewSet

router = DefaultRouter()
router.register(r'detainees', DetaineeViewSet, basename='detainees') 

urlpatterns = [
   path('', include(router.urls)),
]

