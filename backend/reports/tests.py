from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from core.choices import LeadStatus, UserRole
from leads.models import Lead, LeadSource
from customers.models import Customer
from followups.models import FollowUp


class ReportTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@test.com", password="pass", role=UserRole.ADMIN,
        )
        self.exec1 = User.objects.create_user(
            email="exec1@test.com", password="pass", role=UserRole.SALES_EXECUTIVE,
        )
        self.exec2 = User.objects.create_user(
            email="exec2@test.com", password="pass", role=UserRole.SALES_EXECUTIVE,
        )
        self.source = LeadSource.objects.create(name="Website")
        self.source2 = LeadSource.objects.create(name="Referral")

        self.lead1 = Lead.objects.create(
            first_name="A", last_name="B", phone="111", source=self.source,
            status=LeadStatus.NEW, estimated_value=1000,
            assigned_to=self.exec1, created_by=self.admin,
        )
        Lead.objects.create(
            first_name="C", last_name="D", phone="222", source=self.source,
            status=LeadStatus.WON, estimated_value=2000,
            assigned_to=self.exec1, created_by=self.admin,
        )
        Lead.objects.create(
            first_name="E", last_name="F", phone="333", source=self.source2,
            status=LeadStatus.LOST, estimated_value=3000,
            assigned_to=self.exec2, created_by=self.admin,
        )

        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_status_wise_counts(self):
        response = self.client.get("/api/reports/status-wise/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        counts = {r["status"]: r["count"] for r in response.data}
        self.assertEqual(counts["NEW"], 1)
        self.assertEqual(counts["WON"], 1)
        self.assertEqual(counts["LOST"], 1)

    def test_source_wise_counts(self):
        response = self.client.get("/api/reports/source-wise/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        counts = {r["source_name"]: r["count"] for r in response.data}
        self.assertEqual(counts["Website"], 2)
        self.assertEqual(counts["Referral"], 1)

    def test_user_wise_report(self):
        response = self.client.get("/api/reports/user-wise/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_map = {r["user_name"]: r for r in response.data}
        exec1_entry = user_map.get(self.exec1.get_full_name() or self.exec1.email)
        self.assertIsNotNone(exec1_entry)
        self.assertEqual(exec1_entry["total_leads"], 2)
        self.assertEqual(exec1_entry["won_leads"], 1)

    def test_user_wise_report_forbidden_for_exec(self):
        refresh = RefreshToken.for_user(self.exec1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = self.client.get("/api/reports/user-wise/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_date_wise_report(self):
        today = timezone.localdate().isoformat()
        response = self.client.get(
            f"/api/reports/date-wise/?start={today}&end={today}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["leads_created"], 3)

    def test_date_wise_report_no_dates(self):
        response = self.client.get("/api/reports/date-wise/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_date_wise_report_forbidden_for_exec(self):
        refresh = RefreshToken.for_user(self.exec1)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        today = timezone.localdate().isoformat()
        response = self.client.get(
            f"/api/reports/date-wise/?start={today}&end={today}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_status_csv_export(self):
        response = self.client.get("/api/reports/status-wise/?export=csv")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment", response["Content-Disposition"])

    def test_user_csv_export(self):
        response = self.client.get("/api/reports/user-wise/?export=csv")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_source_csv_export(self):
        response = self.client.get("/api/reports/source-wise/?export=csv")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_date_csv_export(self):
        today = timezone.localdate().isoformat()
        response = self.client.get(
            f"/api/reports/date-wise/?start={today}&end={today}&export=csv",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")
