from django.urls import include, path
from rest_framework.routers import DefaultRouter
from cases.views import CaseViewSet

router = DefaultRouter()
router.register(r'cases', CaseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
