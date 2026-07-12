import csv

from django.db.models import Count, Sum
from django.http import HttpResponse
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from core.choices import FollowUpStatus, LeadStatus, UserRole
from customers.models import Customer
from followups.models import FollowUp
from leads.models import Lead, LeadSource


def _export_csv(filename, headers, rows):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    if headers is not None:
        writer.writerow(headers)
    if rows:
        writer.writerows(rows)
    return response


class UserWiseReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in (UserRole.ADMIN, UserRole.SALES_MANAGER):
            return Response(
                {"detail": "You do not have permission to view this report."},
                status=403,
            )

        executives = User.objects.filter(role=UserRole.SALES_EXECUTIVE)
        data = []

        for exec_user in executives:
            exec_leads = Lead.objects.filter(assigned_to=exec_user)
            data.append({
                "user_id": str(exec_user.id),
                "user_name": exec_user.get_full_name() or exec_user.email,
                "total_leads": exec_leads.count(),
                "won_leads": exec_leads.filter(status=LeadStatus.WON).count(),
                "lost_leads": exec_leads.filter(status=LeadStatus.LOST).count(),
                "customers": Customer.objects.filter(
                    lead__assigned_to=exec_user,
                ).count(),
                "pending_followups": FollowUp.objects.filter(
                    assigned_to=exec_user,
                    status=FollowUpStatus.PENDING,
                ).count(),
            })

        if request.query_params.get("export") == "csv":
            return _export_csv(
                "user_wise_report.csv",
                ["User", "Total Leads", "Won", "Lost", "Customers", "Pending Follow-ups"],
                [[r["user_name"], r["total_leads"], r["won_leads"],
                  r["lost_leads"], r["customers"], r["pending_followups"]] for r in data],
            )

        return Response(data)


class StatusWiseReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role in (UserRole.ADMIN, UserRole.SALES_MANAGER):
            leads = Lead.objects.all()
        else:
            leads = Lead.objects.filter(assigned_to=user)

        data = []
        for status_choice in LeadStatus:
            count = leads.filter(status=status_choice).count()
            data.append({
                "status": status_choice.value,
                "label": status_choice.label,
                "count": count,
            })

        if request.query_params.get("export") == "csv":
            return _export_csv(
                "status_wise_report.csv",
                ["Status", "Count"],
                [[r["label"], r["count"]] for r in data],
            )

        return Response(data)


class SourceWiseReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role in (UserRole.ADMIN, UserRole.SALES_MANAGER):
            leads_qs = Lead.objects.all()
        else:
            leads_qs = Lead.objects.filter(assigned_to=user)

        data = []
        for source in LeadSource.objects.all():
            count = leads_qs.filter(source=source).count()
            data.append({
                "source_id": str(source.id),
                "source_name": source.name,
                "count": count,
            })

        if request.query_params.get("export") == "csv":
            return _export_csv(
                "source_wise_report.csv",
                ["Source", "Count"],
                [[r["source_name"], r["count"]] for r in data],
            )

        return Response(data)


class DateWiseReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in (UserRole.ADMIN, UserRole.SALES_MANAGER):
            return Response(
                {"detail": "You do not have permission to view this report."},
                status=403,
            )

        start_date = request.query_params.get("start")
        end_date = request.query_params.get("end")

        if not start_date or not end_date:
            return Response(
                {"detail": "Both 'start' and 'end' query parameters are required."},
                status=400,
            )

        leads = Lead.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        customers = Customer.objects.filter(converted_at__date__gte=start_date, converted_at__date__lte=end_date)
        followups = FollowUp.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)

        data = {
            "start_date": start_date,
            "end_date": end_date,
            "leads_created": leads.count(),
            "customers_converted": customers.count(),
            "followups_created": followups.count(),
            "leads_by_status": {
                s.value: leads.filter(status=s).count()
                for s in LeadStatus
            },
            "pipeline_value": leads.filter(
                status__in=[
                    LeadStatus.NEW,
                    LeadStatus.CONTACTED,
                    LeadStatus.DEMO,
                    LeadStatus.NEGOTIATION,
                ],
            ).aggregate(total=Sum("estimated_value"))["total"] or 0,
        }

        if request.query_params.get("export") == "csv":
            rows = [
                ["Metric", "Value"],
                ["Start Date", start_date],
                ["End Date", end_date],
                ["Leads Created", data["leads_created"]],
                ["Customers Converted", data["customers_converted"]],
                ["Follow-ups Created", data["followups_created"]],
                ["Pipeline Value", data["pipeline_value"]],
            ]
            for status_label, count in data["leads_by_status"].items():
                rows.append([f"Leads - {status_label}", count])
            return _export_csv("date_wise_report.csv", None, rows)

        return Response(data)
