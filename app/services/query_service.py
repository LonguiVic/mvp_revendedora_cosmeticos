from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.installment import Installment
from app.models.profit import Profit
from app.models.sale import Sale


class QueryService:

    def get_receivables(
        self,
        db: Session,
        month: int,
        year: int
    ):

        rows = (
            db.query(
                Sale.customer_name,
                func.sum(Installment.amount)
            )
            .join(
                Installment,
                Sale.id == Installment.sale_id
            )
            .filter(
                Installment.due_month == month,
                Installment.due_year == year,
                Installment.status == "PENDING"
            )
            .group_by(
                Sale.customer_name
            )
            .all()
        )

        total = sum(
            float(row[1])
            for row in rows
        )

        return {
            "total": total,
            "clients": [
                {
                    "cliente": row[0],
                    "valor": float(row[1])
                }
                for row in rows
            ]
        }

    def get_customer_debts(
        self,
        db: Session,
        customer_name: str
    ):

        rows = (
            db.query(
                Sale.customer_name,
                Installment.amount,
                Installment.due_month,
                Installment.due_year
            )
            .join(
                Installment,
                Sale.id == Installment.sale_id
            )
            .filter(
                # Sale.customer_name.ilike(customer_name),
                Sale.customer_name.ilike(
                    f"%{customer_name}%"
                ),
                Installment.status == "PENDING"
            )
            .order_by(
                Installment.due_year,
                Installment.due_month
            )
            .all()
        )

        return {
            "cliente": customer_name,
            "parcelas": [
                {
                    "mes": row.due_month,
                    "ano": row.due_year,
                    "valor": float(row.amount)
                }
                for row in rows
            ]
        }

    def get_monthly_profit(
        self,
        db: Session,
        month: int,
        year: int
    ):

        rows = (
            db.query(
                Profit.revenue,
                Profit.cost,
                Profit.profit
            )
            .filter(
                func.strftime(
                    "%m",
                    Profit.created_at
                ) == f"{month:02d}",
                func.strftime(
                    "%Y",
                    Profit.created_at
                ) == str(year)
            )
            .all()
        )

        revenue = sum(
            float(row.revenue)
            for row in rows
        )

        cost = sum(
            float(row.cost)
            for row in rows
        )

        profit = sum(
            float(row.profit)
            for row in rows
        )

        return {
            "revenue": revenue,
            "cost": cost,
            "profit": profit
        }