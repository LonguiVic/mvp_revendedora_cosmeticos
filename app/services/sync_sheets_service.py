from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.integrations.google_sheets import GoogleSheetsService
from app.models.sale import Sale
from app.models.installment import Installment
from app.models.profit import Profit
from app.models.audit import Audit

MONTH_NAMES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

class SyncSheetsService:

    def sync(self, db: Session):
        sheets = GoogleSheetsService()
        self.sync_monthly_tabs(db, sheets)
        self.sync_profits(db, sheets)
        self.sync_audits(db, sheets)

    def sync_monthly_tabs(self, db: Session, sheets: GoogleSheetsService):
        for month_num, month_name in MONTH_NAMES.items():
            installments = (
                db.query(Installment, Sale)
                .join(Sale, Installment.sale_id == Sale.id)
                .filter(Installment.due_month == month_num)
                .order_by(Installment.due_year, Installment.installment_number)
                .all()
            )

            rows = [
                [
                    "ID da venda", "Data da venda", "Nome do cliente", "Telefone", "Marca",
                    "Produto", "Valor total da venda", "Número da parcela",
                    "Quantidade total de parcelas", "Valor da parcela",
                    "Status do pagamento", "Data do pagamento", "Observações",
                    "Último lembrete enviado", "Cobrança automática habilitada"
                ]
            ]

            for inst, sale in installments:
                payment_date = inst.payment_date.strftime("%d/%m/%Y") if inst.payment_date else ""
                
                products_str = ", ".join([f"{i.quantity}x {i.product}" for i in sale.items])
                brands_str = ", ".join(list(set([i.brand for i in sale.items])))

                rows.append([
                    sale.sale_code,
                    sale.sale_date.strftime("%d/%m/%Y"),
                    sale.customer_name,
                    sale.phone or "",
                    brands_str,
                    products_str,
                    float(sale.sale_value),
                    inst.installment_number,
                    inst.total_installments,
                    float(inst.amount),
                    inst.status,
                    payment_date,
                    "", # Observações
                    "", # Último lembrete enviado
                    "Sim" # Cobrança automática habilitada
                ])

            # Sync even if empty so the sheet is created
            sheets.replace_sheet_data(month_name, rows)
            sheets.format_sheet(month_name)

    def sync_profits(self, db: Session, sheets: GoogleSheetsService):
        profits = (
            db.query(Profit, Sale)
            .join(Sale, Profit.sale_id == Sale.id)
            .order_by(Profit.created_at)
            .all()
        )

        rows = [
            [
                "ID da venda", "Data", "Cliente", "Marca", "Produto",
                "Receita", "Custo", "Lucro", "Status"
            ]
        ]

        for profit, sale in profits:
            products_str = ", ".join([f"{i.quantity}x {i.product}" for i in sale.items])
            brands_str = ", ".join(list(set([i.brand for i in sale.items])))

            rows.append([
                sale.sale_code,
                sale.sale_date.strftime("%d/%m/%Y"),
                sale.customer_name,
                brands_str,
                products_str,
                float(profit.revenue),
                float(profit.cost),
                float(profit.profit),
                profit.status
            ])

        sheets.replace_sheet_data("Lucros", rows)
        sheets.format_sheet("Lucros")

    def sync_audits(self, db: Session, sheets: GoogleSheetsService):
        audits = db.query(Audit).order_by(Audit.created_at).all()
        
        rows = [
            [
                "Data", "Hora", "Tipo de evento", "ID da venda",
                "Usuário", "Observações"
            ]
        ]

        for audit in audits:
            sale = db.query(Sale).filter(Sale.id == audit.sale_id).first()
            sale_code = sale.sale_code if sale else str(audit.sale_id)

            rows.append([
                audit.created_at.strftime("%d/%m/%Y"),
                audit.created_at.strftime("%H:%M:%S"),
                audit.event_type,
                sale_code,
                "Sistema",
                audit.description
            ])

        sheets.replace_sheet_data("Auditoria", rows)
        sheets.format_sheet("Auditoria")
