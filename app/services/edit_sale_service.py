from sqlalchemy.orm import Session
from app.models.sale import Sale, SaleItemModel
from app.models.installment import Installment
from app.models.profit import Profit
from app.models.audit import Audit

class EditSaleService:
    
    def remove_item(self, db: Session, sale_id: int, product_name: str):
        sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            raise ValueError("Venda não encontrada")

        item_to_remove = None
        for item in sale.items:
            if product_name.lower() in item.product.lower():
                item_to_remove = item
                break
        
        if not item_to_remove:
            raise ValueError(f"Item '{product_name}' não encontrado na venda.")

        if len(sale.items) == 1:
            raise ValueError("A venda possui apenas 1 item. Cancele a venda inteira em vez de remover o último item.")

        # Estimate the proportional value of the item to reduce the total
        # In a real app we'd have unit_price and unit_cost on SaleItemModel.
        # Since we don't, we will assume average proportional reduction.
        total_quantity = sum([i.quantity for i in sale.items])
        item_ratio = item_to_remove.quantity / total_quantity

        value_reduction = sale.sale_value * item_ratio
        cost_reduction = sale.cost_value * item_ratio
        profit_reduction = value_reduction - cost_reduction

        sale.sale_value -= value_reduction
        sale.cost_value -= cost_reduction
        sale.profit_value -= profit_reduction

        db.delete(item_to_remove)
        db.flush()

        # Update installments
        installments = db.query(Installment).filter(Installment.sale_id == sale.id).all()
        new_installment_amount = sale.sale_value / sale.installments
        for inst in installments:
            inst.amount = new_installment_amount

        # Update profit
        profit_record = db.query(Profit).filter(Profit.sale_id == sale.id).first()
        if profit_record:
            profit_record.revenue = sale.sale_value
            profit_record.cost = sale.cost_value
            profit_record.profit = sale.profit_value

        audit = Audit(
            event_type="ITEM_REMOVED",
            sale_id=sale.id,
            description=f"Item '{item_to_remove.product}' removido da venda."
        )
        db.add(audit)
        db.commit()
        db.refresh(sale)
        return sale
