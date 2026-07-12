from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FollowUpViewSet

router = DefaultRouter()
router.register("", FollowUpViewSet, basename="followup")

urlpatterns = [
    path("", include(router.urls)),
]
