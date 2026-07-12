from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from core.choices import LeadStatus, UserRole
from leads.models import Lead, LeadSource
from .models import Customer


class CustomerConversionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@test.com", password="pass", role=UserRole.ADMIN,
        )
        self.exec = User.objects.create_user(
            email="exec@test.com", password="pass", role=UserRole.SALES_EXECUTIVE,
        )
        self.source = LeadSource.objects.create(name="Website")
        self.lead = Lead.objects.create(
            first_name="John", last_name="Doe",
            email="john@example.com", phone="1234567890",
            company="Acme Inc",
            source=self.source, status=LeadStatus.WON,
            assigned_to=self.exec, created_by=self.admin,
        )
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_convert_won_lead(self):
        response = self.client.post(f"/api/leads/leads/{self.lead.id}/convert/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        customer = Customer.objects.first()
        self.assertEqual(customer.first_name, "John")
        self.assertEqual(customer.last_name, "Doe")
        self.assertEqual(customer.email, "john@example.com")
        self.assertEqual(customer.phone, "1234567890")
        self.assertEqual(customer.company, "Acme Inc")

    def test_cannot_convert_lost_lead(self):
        lost_lead = Lead.objects.create(
            first_name="Lost", last_name="Lead", phone="5551111",
            source=self.source, status=LeadStatus.LOST,
            assigned_to=self.exec, created_by=self.admin,
        )
        response = self.client.post(f"/api/leads/leads/{lost_lead.id}/convert/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Customer.objects.count(), 0)

    def test_cannot_convert_twice(self):
        self.client.post(f"/api/leads/leads/{self.lead.id}/convert/")
        response = self.client.post(f"/api/leads/leads/{self.lead.id}/convert/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Customer.objects.count(), 1)

    def test_cannot_convert_non_won_lead(self):
        new_lead = Lead.objects.create(
            first_name="New", last_name="Lead", phone="5552222",
            source=self.source, status=LeadStatus.NEW,
            assigned_to=self.exec, created_by=self.admin,
        )
        response = self.client.post(f"/api/leads/leads/{new_lead.id}/convert/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CustomerViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/customers/"
        self.admin = User.objects.create_user(
            email="admin@test.com", password="pass", role=UserRole.ADMIN,
        )
        self.exec = User.objects.create_user(
            email="exec@test.com", password="pass", role=UserRole.SALES_EXECUTIVE,
        )
        self.source = LeadSource.objects.create(name="Web")
        self.lead = Lead.objects.create(
            first_name="John", last_name="Doe", phone="9998888",
            source=self.source, status=LeadStatus.WON,
            assigned_to=self.exec, created_by=self.admin,
        )

    def _auth(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_list_customers_admin(self):
        self._auth(self.admin)
        Customer.objects.create(lead=self.lead, first_name="John",
                                last_name="Doe", phone="9998888",
                                created_by=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
