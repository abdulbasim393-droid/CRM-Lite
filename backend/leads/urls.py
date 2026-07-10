from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LeadSourceViewSet,
    LeadViewSet,
)

router = DefaultRouter()

router.register(
    "lead-sources",
    LeadSourceViewSet,
)

router.register(
    "leads",
    LeadViewSet,
)

urlpatterns = [
    path("", include(router.urls)),
]