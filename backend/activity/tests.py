from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from core.choices import LeadStatus, UserRole
from leads.models import Lead, LeadSource, LeadNote
from customers.models import Customer
from followups.models import FollowUp
from .models import ActivityLog, ActionType, EntityType


class ActivityLoggingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@test.com", password="pass", role=UserRole.ADMIN,
        )
        self.exec = User.objects.create_user(
            email="exec@test.com", password="pass", role=UserRole.SALES_EXECUTIVE,
        )
        self.source = LeadSource.objects.create(name="Web")
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def _create_lead(self, **kwargs):
        data = {
            "first_name": "John", "last_name": "Doe", "phone": "111111",
            "source": str(self.source.id), "assigned_to": str(self.exec.id),
            **kwargs,
        }
        return self.client.post("/api/leads/leads/", data, format="json")

    def test_log_on_lead_create(self):
        response = self._create_lead()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        log = ActivityLog.objects.filter(
            entity_type=EntityType.LEAD, action=ActionType.CREATED,
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(str(log.performed_by_id), str(self.admin.id))

    def test_log_on_lead_update(self):
        resp = self._create_lead()
        lead_id = resp.data["id"]
        response = self.client.patch(
            f"/api/leads/leads/{lead_id}/",
            {"first_name": "Jane"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        log = ActivityLog.objects.filter(
            entity_type=EntityType.LEAD, action=ActionType.UPDATED,
        ).first()
        self.assertIsNotNone(log)

    def test_log_on_lead_delete(self):
        resp = self._create_lead()
        lead_id = resp.data["id"]
        response = self.client.delete(f"/api/leads/leads/{lead_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        log = ActivityLog.objects.filter(
            entity_type=EntityType.LEAD, action=ActionType.DELETED,
        ).first()
        self.assertIsNotNone(log)

    def test_log_on_lead_convert(self):
        resp = self._create_lead(status=LeadStatus.WON)
        lead_id = resp.data["id"]
        response = self.client.post(f"/api/leads/leads/{lead_id}/convert/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        convert_log = ActivityLog.objects.filter(
            entity_type=EntityType.LEAD, action=ActionType.CONVERTED,
        ).first()
        self.assertIsNotNone(convert_log)
        customer_log = ActivityLog.objects.filter(
            entity_type=EntityType.CUSTOMER, action=ActionType.CREATED,
        ).first()
        self.assertIsNotNone(customer_log)

    def test_log_on_note_create(self):
        resp = self._create_lead()
        lead_id = resp.data["id"]
        response = self.client.post(
            "/api/leads/lead-notes/",
            {"lead": lead_id, "note_type": "CALL", "note_text": "Test call"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        log = ActivityLog.objects.filter(
            entity_type=EntityType.LEAD_NOTE, action=ActionType.CREATED,
        ).first()
        self.assertIsNotNone(log)

    def test_log_on_note_update(self):
        resp = self._create_lead()
        lead_id = resp.data["id"]
        note_resp = self.client.post(
            "/api/leads/lead-notes/",
            {"lead": lead_id, "note_type": "CALL", "note_text": "Original"},
            format="json",
        )
        note_id = note_resp.data["id"]
        self.client.patch(
            f"/api/leads/lead-notes/{note_id}/",
            {"note_text": "Updated"},
            format="json",
        )
        log = ActivityLog.objects.filter(
            entity_type=EntityType.LEAD_NOTE, action=ActionType.UPDATED,
        ).first()
        self.assertIsNotNone(log)

    def test_log_on_note_delete(self):
        resp = self._create_lead()
        lead_id = resp.data["id"]
        note_resp = self.client.post(
            "/api/leads/lead-notes/",
            {"lead": lead_id, "note_type": "CALL", "note_text": "Delete me"},
            format="json",
        )
        note_id = note_resp.data["id"]
        self.client.delete(f"/api/leads/lead-notes/{note_id}/")
        log = ActivityLog.objects.filter(
            entity_type=EntityType.LEAD_NOTE, action=ActionType.DELETED,
        ).first()
        self.assertIsNotNone(log)

    def test_log_on_followup_complete(self):
        resp = self._create_lead()
        lead_id = resp.data["id"]
        from datetime import timedelta
        from django.utils import timezone
        fu_resp = self.client.post(
            "/api/followups/",
            {
                "lead": lead_id,
                "assigned_to": str(self.exec.id),
                "follow_up_at": (timezone.now() + timedelta(hours=24)).isoformat(),
                "purpose": "Follow-up test",
            },
            format="json",
        )
        fu_id = fu_resp.data["id"]
        self.client.patch(
            f"/api/followups/{fu_id}/complete/",
            {"outcome": "Done"},
            format="json",
        )
        log = ActivityLog.objects.filter(
            entity_type=EntityType.FOLLOW_UP, action=ActionType.COMPLETED,
        ).first()
        self.assertIsNotNone(log)


class ActivityLogAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/activity/activity-logs/"
        self.admin = User.objects.create_user(
            email="admin@test.com", password="pass", role=UserRole.ADMIN,
        )
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_list_logs(self):
        ActivityLog.objects.create(
            entity_type=EntityType.LEAD, entity_id="00000000-0000-0000-0000-000000000001",
            action=ActionType.CREATED, performed_by=self.admin,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
