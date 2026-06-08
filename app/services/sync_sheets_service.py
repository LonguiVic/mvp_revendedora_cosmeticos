from sqlalchemy.orm import Session
from sqlalchemy import func

from app.integrations.google_sheets import (
    GoogleSheetsService
)

from app.models.sale import Sale
from app.models.installment import Installment
from app.models.profit import Profit


class SyncSheetsService:

    def sync(
        self,
        db: Session
    ):

        sheets = GoogleSheetsService()

        self.sync_sales(
            db,
            sheets
        )

        self.sync_installments(
            db,
            sheets
        )

        self.sync_profits(
            db,
            sheets
        )

        self.sync_receivables(
            db,
            sheets
        )

        self.sync_dashboard(
            db,
            sheets
        )

    def sync_sales(
        self,
        db,
        sheets
    ):

        sales = (
            db.query(Sale)
            .all()
        )

        rows = [
            [
                "sale_id",
                "sale_code",
                "cliente",
                "produto",
                "valor",
                "lucro",
                "status"
            ]
        ]

        for sale in sales:

            rows.append(
                [
                    sale.id,
                    sale.sale_code,
                    sale.customer_name,
                    sale.product,
                    sale.sale_value,
                    sale.profit_value,
                    sale.status
                ]
            )

        sheets.replace_sheet_data(
            "sales",
            rows
        )

        sheets.format_sheet(
            "sales"
        )

    def sync_installments(
        self,
        db,
        sheets
    ):

        installments = (
            db.query(Installment)
            .all()
        )

        rows = [
            [
                "id",
                "sale_id",
                "numero",
                "total",
                "valor",
                "mes",
                "ano",
                "status"
            ]
        ]

        for i in installments:

            rows.append(
                [
                    i.id,
                    i.sale_id,
                    i.installment_number,
                    i.total_installments,
                    i.amount,
                    i.due_month,
                    i.due_year,
                    i.status
                ]
            )

        sheets.replace_sheet_data(
            "installments",
            rows
        )

        sheets.format_sheet(
            "installments"
        )

    def sync_profits(
        self,
        db,
        sheets
    ):

        profits = (
            db.query(Profit)
            .join(
                Sale,
                Sale.id == Profit.sale_id
            )
            .filter(
                Sale.status == "ACTIVE"
            )
            .all()
        )

        rows = [
            [
                "sale_id",
                "receita",
                "custo",
                "lucro"
            ]
        ]

        for p in profits:

            rows.append(
                [
                    p.sale_id,
                    p.revenue,
                    p.cost,
                    p.profit
                ]
            )

        sheets.replace_sheet_data(
            "profits",
            rows
        )

        sheets.format_sheet(
            "profits"
        )

    def sync_receivables(
        self,
        db,
        sheets
    ):
        rows_db = (
            db.query(
                Installment.due_month,
                Installment.due_year,
                func.sum(
                    Installment.amount
                )
            )
            .filter(
                Installment.status == "PENDING"
            )
            .group_by(
                Installment.due_month,
                Installment.due_year
            )
            .order_by(
                Installment.due_year,
                Installment.due_month
            )
            .all()
        )

        rows = [
            [
                "mes",
                "ano",
                "valor_a_receber"
            ]
        ]

        for row in rows_db:

            rows.append(
                [
                    row.due_month,
                    row.due_year,
                    float(row[2])
                ]
            )

        sheets.replace_sheet_data(
            "receivables",
            rows
        )

        sheets.format_sheet(
            "receivables"
        )

    def sync_dashboard(
        self,
        db,
        sheets
    ):

        total_sales = (
            db.query(Sale)
            .filter(
                Sale.status == "ACTIVE"
            )
            .count()
        )

        revenue = (
            db.query(
                func.sum(
                    Sale.sale_value
                )
            )
            .filter(
                Sale.status == "ACTIVE"
            )
            .scalar()
            or 0
        )

        cost = (
            db.query(
                func.sum(
                    Sale.cost_value
                )
            )
            .filter(
                Sale.status == "ACTIVE"
            )
            .scalar()
            or 0
        )

        profit = (
            db.query(
                func.sum(
                    Sale.profit_value
                )
            )
            .filter(
                Sale.status == "ACTIVE"
            )
            .scalar()
            or 0
        )

        pending_installments = (
            db.query(
                Installment
            )
            .filter(
                Installment.status == "PENDING"
            )
            .count()
        )

        receivables = (
            db.query(
                func.sum(
                    Installment.amount
                )
            )
            .filter(
                Installment.status == "PENDING"
            )
            .scalar()
            or 0
        )

        debtors = (
            db.query(
                Sale.customer_name
            )
            .join(
                Installment,
                Sale.id == Installment.sale_id
            )
            .filter(
                Installment.status == "PENDING"
            )
            .distinct()
            .count()
        )

        rows = [
            ["Métrica", "Valor"],
            ["Total de vendas", total_sales],
            ["Receita total", float(revenue)],
            ["Custo total", float(cost)],
            ["Lucro total", float(profit)],
            ["Parcelas pendentes", pending_installments],
            ["Valor a receber", float(receivables)],
            ["Clientes devedores", debtors]
        ]

        sheets.replace_sheet_data(
            "dashboard",
            rows
        )

        sheets.format_sheet(
            "dashboard"
        )