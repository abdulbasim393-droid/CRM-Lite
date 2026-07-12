from django.urls import path

from .views import (
    DateWiseReportView,
    SourceWiseReportView,
    StatusWiseReportView,
    UserWiseReportView,
)

urlpatterns = [
    path("user-wise/", UserWiseReportView.as_view(), name="report-user-wise"),
    path("status-wise/", StatusWiseReportView.as_view(), name="report-status-wise"),
    path("source-wise/", SourceWiseReportView.as_view(), name="report-source-wise"),
    path("date-wise/", DateWiseReportView.as_view(), name="report-date-wise"),
]
