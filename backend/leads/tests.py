from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from core.choices import LeadPriority, LeadStatus, UserRole
from .models import Lead, LeadSource


class LeadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.leads_url = "/api/leads/leads/"
        self.sources_url = "/api/leads/lead-sources/"

        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="pass123",
            role=UserRole.ADMIN,
        )
        self.manager = User.objects.create_user(
            email="manager@test.com",
            password="pass123",
            role=UserRole.SALES_MANAGER,
        )
        self.exec1 = User.objects.create_user(
            email="exec1@test.com",
            password="pass123",
            role=UserRole.SALES_EXECUTIVE,
        )
        self.exec2 = User.objects.create_user(
            email="exec2@test.com",
            password="pass123",
            role=UserRole.SALES_EXECUTIVE,
        )

        self.source = LeadSource.objects.create(name="Website")

        self.lead_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "company": "Acme Inc",
            "source": str(self.source.id),
            "status": LeadStatus.NEW,
            "priority": LeadPriority.HIGH,
            "estimated_value": "5000.00",
        }

    def _auth(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_admin_create_lead(self):
        self._auth(self.admin)
        data = {**self.lead_data, "assigned_to": str(self.exec1.id)}
        response = self.client.post(self.leads_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lead.objects.count(), 1)

    def test_admin_create_lead_without_assigned_to(self):
        self._auth(self.admin)
        response = self.client.post(self.leads_url, self.lead_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_exec_auto_assigns_self(self):
        self._auth(self.exec1)
        response = self.client.post(self.leads_url, self.lead_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        lead = Lead.objects.first()
        self.assertEqual(lead.assigned_to, self.exec1)
        self.assertEqual(lead.created_by, self.exec1)

    def test_list_leads_admin_sees_all(self):
        self._auth(self.admin)
        Lead.objects.create(
            first_name="A", last_name="B", phone="111", source=self.source,
            assigned_to=self.exec1, created_by=self.admin,
        )
        Lead.objects.create(
            first_name="C", last_name="D", phone="222", source=self.source,
            assigned_to=self.exec2, created_by=self.admin,
        )
        response = self.client.get(self.leads_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_leads_exec_sees_only_own(self):
        self._auth(self.exec1)
        Lead.objects.create(
            first_name="A", last_name="B", phone="111", source=self.source,
            assigned_to=self.exec1, created_by=self.admin,
        )
        Lead.objects.create(
            first_name="C", last_name="D", phone="222", source=self.source,
            assigned_to=self.exec2, created_by=self.admin,
        )
        response = self.client.get(self.leads_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_lead(self):
        self._auth(self.admin)
        lead = Lead.objects.create(
            first_name="Old", last_name="Name", phone="333", source=self.source,
            assigned_to=self.exec1, created_by=self.admin,
        )
        response = self.client.patch(
            f"{self.leads_url}{lead.id}/",
            {"first_name": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lead.refresh_from_db()
        self.assertEqual(lead.first_name, "Updated")

    def test_exec_cannot_update_assigned_to(self):
        self._auth(self.exec1)
        lead = Lead.objects.create(
            first_name="Test", last_name="User", phone="444", source=self.source,
            assigned_to=self.exec1, created_by=self.admin,
        )
        response = self.client.patch(
            f"{self.leads_url}{lead.id}/",
            {"assigned_to": str(self.exec2.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_delete_lead(self):
        self._auth(self.admin)
        lead = Lead.objects.create(
            first_name="Del", last_name="Me", phone="555", source=self.source,
            assigned_to=self.exec1, created_by=self.admin,
        )
        response = self.client.delete(f"{self.leads_url}{lead.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lead.objects.count(), 0)

    def test_exec_cannot_delete_lead(self):
        self._auth(self.exec1)
        lead = Lead.objects.create(
            first_name="Del", last_name="Me", phone="666", source=self.source,
            assigned_to=self.exec1, created_by=self.admin,
        )
        response = self.client.delete(f"{self.leads_url}{lead.id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_phone_rejected(self):
        self._auth(self.admin)
        data = {**self.lead_data, "assigned_to": str(self.exec1.id)}
        self.client.post(self.leads_url, data, format="json")
        response = self.client.post(self.leads_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_rejected(self):
        self._auth(self.admin)
        data = {**self.lead_data, "assigned_to": str(self.exec1.id)}
        self.client.post(self.leads_url, data, format="json")
        data2 = {
            **self.lead_data, "phone": "9999999999", "assigned_to": str(self.exec1.id),
        }
        response = self.client.post(self.leads_url, data2, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_status(self):
        self._auth(self.admin)
        Lead.objects.create(
            first_name="A", last_name="B", phone="771", source=self.source,
            status=LeadStatus.NEW, assigned_to=self.exec1, created_by=self.admin,
        )
        Lead.objects.create(
            first_name="C", last_name="D", phone="772", source=self.source,
            status=LeadStatus.WON, assigned_to=self.exec2, created_by=self.admin,
        )
        response = self.client.get(f"{self.leads_url}?status=WON")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_by_name(self):
        self._auth(self.admin)
        Lead.objects.create(
            first_name="Alice", last_name="Smith", phone="881", source=self.source,
            assigned_to=self.exec1, created_by=self.admin,
        )
        Lead.objects.create(
            first_name="Bob", last_name="Jones", phone="882", source=self.source,
            assigned_to=self.exec1, created_by=self.admin,
        )
        response = self.client.get(f"{self.leads_url}?search=Alice")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_ordering(self):
        self._auth(self.admin)
        Lead.objects.create(
            first_name="Old", last_name="Lead", phone="991", source=self.source,
            estimated_value=100, assigned_to=self.exec1, created_by=self.admin,
        )
        Lead.objects.create(
            first_name="New", last_name="Lead", phone="992", source=self.source,
            estimated_value=200, assigned_to=self.exec1, created_by=self.admin,
        )
        response = self.client.get(f"{self.leads_url}?ordering=estimated_value")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data
        self.assertEqual(len(results), 2)
        values = [r["estimated_value"] for r in results]
        self.assertEqual(values, sorted(values))

    def test_list_returns_all(self):
        self._auth(self.admin)
        for i in range(25):
            Lead.objects.create(
                first_name=f"User{i}", last_name="X", phone=f"555{i:04d}",
                source=self.source, assigned_to=self.exec1, created_by=self.admin,
            )
        response = self.client.get(self.leads_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 25)


class LeadSourceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/leads/lead-sources/"
        self.admin = User.objects.create_user(
            email="admin@test.com", password="pass", role=UserRole.ADMIN,
        )
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_create_source(self):
        response = self.client.post(self.url, {"name": "Referral"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_sources(self):
        LeadSource.objects.create(name="Website")
        LeadSource.objects.create(name="Referral")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class LeadNoteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/leads/lead-notes/"
        self.admin = User.objects.create_user(
            email="admin@test.com", password="pass", role=UserRole.ADMIN,
        )
        self.exec = User.objects.create_user(
            email="exec@test.com", password="pass", role=UserRole.SALES_EXECUTIVE,
        )
        self.source = LeadSource.objects.create(name="Web")
        self.lead = Lead.objects.create(
            first_name="Test", last_name="Lead", phone="1234", source=self.source,
            assigned_to=self.exec, created_by=self.admin,
        )
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_create_note(self):
        response = self.client.post(
            self.url,
            {"lead": str(self.lead.id), "note_type": "CALL", "note_text": "Called customer"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_notes(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
