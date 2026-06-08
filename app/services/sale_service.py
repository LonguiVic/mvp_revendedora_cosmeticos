from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.models.installment import Installment


class SaleService:

    def list_sales(
        self,
        db: Session,
        status: str | None = None,
        customer_name: str | None = None
    ):

        query = db.query(Sale)

        if status:

            query = query.filter(
                Sale.status == status.upper()
            )

        if customer_name:

            query = query.filter(
                Sale.customer_name.ilike(
                    f"%{customer_name}%"
                )
            )

        sales = query.order_by(Sale.created_at.desc()).all()

        results = []
        for sale in sales:
            paid_installments = (
                db.query(Installment)
                .filter(
                    Installment.sale_id == sale.id,
                    Installment.status == "PAID"
                )
                .count()
            )

            pending_installments = (
                db.query(Installment)
                .filter(
                    Installment.sale_id == sale.id,
                    Installment.status == "PENDING"
                )
                .count()
            )

            cancelled_installments = (
                db.query(Installment)
                .filter(
                    Installment.sale_id == sale.id,
                    Installment.status == "CANCELLED"
                )
                .count()
            )

            results.append({
                "sale_id": sale.id,
                "sale_code": sale.sale_code,
                "cliente": sale.customer_name,
                "telefone": sale.phone,
                "marca": sale.brand,
                "produto": sale.product,
                "quantidade": sale.quantity,
                "valor_venda": sale.sale_value,
                "custo": sale.cost_value,
                "lucro": sale.profit_value,
                "parcelas": sale.installments,
                "parcelas_pagas": paid_installments,
                "parcelas_pendentes": pending_installments,
                "parcelas_canceladas": cancelled_installments,
                "status": sale.status,
                "data_venda": sale.sale_date.isoformat(),
                "criado_em": sale.created_at.isoformat()
            })

        return results