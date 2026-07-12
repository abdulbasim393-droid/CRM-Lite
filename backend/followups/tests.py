from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from core.choices import LeadStatus, UserRole
from leads.models import Lead, LeadSource
from .models import FollowUp, FollowUpStatus


class FollowUpTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/followups/"
        self.admin = User.objects.create_user(
            email="admin@test.com", password="pass", role=UserRole.ADMIN,
        )
        self.exec = User.objects.create_user(
            email="exec@test.com", password="pass", role=UserRole.SALES_EXECUTIVE,
        )
        self.source = LeadSource.objects.create(name="Web")
        self.lead = Lead.objects.create(
            first_name="Test", last_name="Lead", phone="1234",
            source=self.source, status=LeadStatus.NEW,
            assigned_to=self.exec, created_by=self.admin,
        )
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def _future_time(self):
        return timezone.now() + timedelta(hours=24)

    def test_create_future_followup(self):
        response = self.client.post(
            self.url,
            {
                "lead": str(self.lead.id),
                "assigned_to": str(self.exec.id),
                "follow_up_at": self._future_time().isoformat(),
                "purpose": "Call to follow up",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FollowUp.objects.count(), 1)

    def test_reject_past_date(self):
        past = timezone.now() - timedelta(hours=1)
        response = self.client.post(
            self.url,
            {
                "lead": str(self.lead.id),
                "assigned_to": str(self.exec.id),
                "follow_up_at": past.isoformat(),
                "purpose": "Past follow-up",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_won_lead(self):
        won_lead = Lead.objects.create(
            first_name="Won", last_name="Lead", phone="5555",
            source=self.source, status=LeadStatus.WON,
            assigned_to=self.exec, created_by=self.admin,
        )
        response = self.client.post(
            self.url,
            {
                "lead": str(won_lead.id),
                "assigned_to": str(self.exec.id),
                "follow_up_at": self._future_time().isoformat(),
                "purpose": "Should be rejected",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_lost_lead(self):
        lost_lead = Lead.objects.create(
            first_name="Lost", last_name="Lead", phone="6666",
            source=self.source, status=LeadStatus.LOST,
            assigned_to=self.exec, created_by=self.admin,
        )
        response = self.client.post(
            self.url,
            {
                "lead": str(lost_lead.id),
                "assigned_to": str(self.exec.id),
                "follow_up_at": self._future_time().isoformat(),
                "purpose": "Should be rejected",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complete_followup(self):
        follow_up = FollowUp.objects.create(
            lead=self.lead, assigned_to=self.exec,
            follow_up_at=self._future_time(),
            purpose="Test follow-up",
        )
        response = self.client.patch(
            f"{self.url}{follow_up.id}/complete/",
            {"outcome": "Customer interested"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        follow_up.refresh_from_db()
        self.assertEqual(follow_up.status, FollowUpStatus.COMPLETED)
        self.assertEqual(follow_up.outcome, "Customer interested")
        self.assertIsNotNone(follow_up.completed_at)

    def test_complete_already_completed(self):
        follow_up = FollowUp.objects.create(
            lead=self.lead, assigned_to=self.exec,
            follow_up_at=self._future_time(),
            purpose="Test", status=FollowUpStatus.COMPLETED,
            completed_at=timezone.now(),
        )
        response = self.client.patch(
            f"{self.url}{follow_up.id}/complete/",
            {"outcome": "Still interested"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complete_without_outcome(self):
        follow_up = FollowUp.objects.create(
            lead=self.lead, assigned_to=self.exec,
            follow_up_at=self._future_time(),
            purpose="Test",
        )
        response = self.client.patch(
            f"{self.url}{follow_up.id}/complete/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_followups(self):
        FollowUp.objects.create(
            lead=self.lead, assigned_to=self.exec,
            follow_up_at=self._future_time(), purpose="First",
        )
        FollowUp.objects.create(
            lead=self.lead, assigned_to=self.exec,
            follow_up_at=self._future_time(), purpose="Second",
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
