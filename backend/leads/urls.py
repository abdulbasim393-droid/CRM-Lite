from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LeadSourceViewSet,
    LeadViewSet,
    LeadNoteViewSet,
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

router.register(
    "lead-notes",
    LeadNoteViewSet,
)

urlpatterns = [
    path("", include(router.urls)),
]