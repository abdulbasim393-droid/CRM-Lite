from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ActivityLogViewSet

router = DefaultRouter()

router.register(
    "activity-logs",
    ActivityLogViewSet,
    basename="activity-log",
)

urlpatterns = [
    path("", include(router.urls)),
]