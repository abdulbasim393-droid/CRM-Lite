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


class DashboardTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/dashboard/"
        self.admin = User.objects.create_user(
            email="admin@test.com", password="pass", role=UserRole.ADMIN,
        )
        self.manager = User.objects.create_user(
            email="manager@test.com", password="pass", role=UserRole.SALES_MANAGER,
        )
        self.exec1 = User.objects.create_user(
            email="exec1@test.com", password="pass", role=UserRole.SALES_EXECUTIVE,
        )
        self.exec2 = User.objects.create_user(
            email="exec2@test.com", password="pass", role=UserRole.SALES_EXECUTIVE,
        )
        self.source = LeadSource.objects.create(name="Web")

        Lead.objects.create(
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
            first_name="E", last_name="F", phone="333", source=self.source,
            status=LeadStatus.LOST, estimated_value=3000,
            assigned_to=self.exec2, created_by=self.admin,
        )

    def _auth(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_admin_sees_all_data(self):
        self._auth(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_leads"], 3)
        self.assertEqual(response.data["converted_leads"], 0)
        self.assertEqual(response.data["lost_leads"], 1)

    def test_exec_sees_only_own_data(self):
        self._auth(self.exec1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_leads"], 2)
        self.assertEqual(response.data["lost_leads"], 0)

    def test_pipeline_value(self):
        self._auth(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.data["pipeline_value"], 1000)

    def test_conversion_rate(self):
        self._auth(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.data["total_leads"], 3)
        self.assertEqual(response.data["conversion_rate"], 0.0)

        Customer.objects.create(
            lead=Lead.objects.get(phone="222"),
            first_name="C", last_name="D", phone="222",
            created_by=self.admin,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.data["converted_leads"], 1)
        self.assertEqual(response.data["conversion_rate"], round(1 / 3 * 100, 1))

    def test_today_followups(self):
        self._auth(self.admin)
        now = timezone.now()
        FollowUp.objects.create(
            lead=Lead.objects.first(), assigned_to=self.exec1,
            follow_up_at=now, purpose="Today",
        )
        FollowUp.objects.create(
            lead=Lead.objects.first(), assigned_to=self.exec2,
            follow_up_at=now + timedelta(days=1), purpose="Tomorrow",
        )
        response = self.client.get(self.url)
        self.assertEqual(response.data["today_followups"], 1)

    def test_overdue_followups(self):
        self._auth(self.admin)
        FollowUp.objects.create(
            lead=Lead.objects.first(), assigned_to=self.exec1,
            follow_up_at=timezone.now() - timedelta(hours=2),
            purpose="Overdue",
        )
        response = self.client.get(self.url)
        self.assertEqual(response.data["overdue_followups"], 1)

    def test_unauthenticated_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
