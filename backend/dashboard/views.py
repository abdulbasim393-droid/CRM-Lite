from django.db.models import Sum
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.choices import FollowUpStatus, LeadStatus, UserRole
from customers.models import Customer
from followups.models import FollowUp
from leads.models import Lead


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role in (UserRole.ADMIN, UserRole.SALES_MANAGER):
            leads = Lead.objects.all()
            customers = Customer.objects.all()
            followups = FollowUp.objects.all()
        else:
            leads = Lead.objects.filter(assigned_to=user)
            customers = Customer.objects.filter(lead__assigned_to=user)
            followups = FollowUp.objects.filter(assigned_to=user)

        total_leads = leads.count()
        converted_leads = customers.count()
        lost_leads = leads.filter(status=LeadStatus.LOST).count()

        today = timezone.localdate()
        now = timezone.now()

        today_followups = followups.filter(
            follow_up_at__date=today,
        ).count()

        overdue_followups = followups.filter(
            follow_up_at__lt=now,
            status=FollowUpStatus.PENDING,
        ).count()

        pipeline_value = leads.filter(
            status__in=[
                LeadStatus.NEW,
                LeadStatus.CONTACTED,
                LeadStatus.DEMO,
                LeadStatus.NEGOTIATION,
            ],
        ).aggregate(total=Sum("estimated_value"))["total"] or 0

        conversion_rate = (
            round((converted_leads / total_leads) * 100, 1)
            if total_leads > 0
            else 0.0
        )

        return Response({
            "total_leads": total_leads,
            "converted_leads": converted_leads,
            "lost_leads": lost_leads,
            "today_followups": today_followups,
            "overdue_followups": overdue_followups,
            "pipeline_value": pipeline_value,
            "conversion_rate": conversion_rate,
        })
