"""
Report Delivery Service
"""

from datetime import date, timedelta

from app.config import settings
from app.models.report_subscription import ReportSubscription
from app.services.graph_service import GraphService
from app.services.sales_report_service import SalesReportService


class ReportDeliveryService:
    def __init__(self) -> None:
        self._sales = SalesReportService()

    @staticmethod
    def _current_week_range() -> tuple[str, str]:
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        return monday.isoformat(), sunday.isoformat()

    async def build_payload(self, sub: ReportSubscription) -> tuple[str, str, list[dict]]:
        from_date, to_date = self._current_week_range()

        if sub.report_type == "franchise_summary":
            data = await self._sales.get_franchise_report_data(
                from_date=from_date,
                to_date=to_date,
                include_vat=sub.include_vat,
                department_ids=list(sub.department_ids_json or []),
            )
            subject = f"Franchise sammendrag {from_date} - {to_date}"
            html = (
                f"<h2>Franchise sammendrag</h2>"
                f"<p>Periode: {from_date} - {to_date}</p>"
                f"<p>Totalt salg: {data['summary']['total_sales']}</p>"
                f"<p>Total omsetning: {data['summary']['total_revenue']:.2f} kr</p>"
            )
            return subject, html, []

        # Default: best performers
        data = await self._sales.get_best_performers_data(
            from_date=from_date,
            to_date=to_date,
            include_vat=sub.include_vat,
            department_ids=list(sub.department_ids_json or []),
        )
        excel = await self._sales.build_best_performers_report(
            from_date=from_date,
            to_date=to_date,
            include_vat=sub.include_vat,
            department_ids=list(sub.department_ids_json or []),
        )
        subject = f"Best performers {from_date} - {to_date}"
        top_broker = (data.get("eiendomsmegler") or [{}])[0]
        html = (
            "<h2>Best performers</h2>"
            f"<p>Periode: {from_date} - {to_date}</p>"
            f"<p>Topp megler: {top_broker.get('name', '—')} ({top_broker.get('total_revenue', 0)} kr)</p>"
            "<p>Se vedlagt Excel for full rapport.</p>"
        )
        attachments = [
            {
                "filename": f"best_performers_{from_date}_{to_date}.xlsx",
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "content_bytes": excel,
            }
        ]
        return subject, html, attachments

    async def send_subscription(self, sub: ReportSubscription, *, override_recipient: str | None = None) -> bool:
        sender = settings.MICROSOFT_SENDER_EMAIL or ""
        recipients = [override_recipient] if override_recipient else list(sub.recipients_json or [])
        if not sender or not recipients:
            return False

        subject, html, attachments = await self.build_payload(sub)
        return await GraphService.send_mail(
            sender_email=sender,
            recipient_email=recipients[0],
            recipient_emails=recipients,
            subject=subject,
            html_body=html,
            attachments=attachments,
        )
