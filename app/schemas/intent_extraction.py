from enum import Enum
from pydantic import BaseModel, Field

class Intent(str, Enum):
    REGISTRAR_VENDA = "REGISTRAR_VENDA"
    REGISTRAR_PAGAMENTO = "REGISTRAR_PAGAMENTO"
    CANCELAR_VENDA = "CANCELAR_VENDA"
    CONSULTAR_RECEBIMENTOS = "CONSULTAR_RECEBIMENTOS"
    CONSULTAR_DIVIDA = "CONSULTAR_DIVIDA"
    CONSULTAR_PROXIMAS_COBRANCAS = "CONSULTAR_PROXIMAS_COBRANCAS"
    CONSULTAR_LUCRO = "CONSULTAR_LUCRO"
    CONSULTAR_VENDAS = "CONSULTAR_VENDAS"
    REMOVER_ITEM_VENDA = "REMOVER_ITEM_VENDA"
    OUTROS = "OUTROS"

class IntentExtraction(BaseModel):
    intent: Intent
    cliente: str | None = Field(default=None, description="Nome do cliente, se aplicável")
    mes: str | None = Field(default=None, description="Nome do mês ou número do mês, se aplicável")
    sale_code: str | None = Field(default=None, description="Código da venda (ex: VEN-20260606-001) caso seja um cancelamento")
    produto: str | None = Field(default=None, description="Nome do produto, se aplicável (ex: para remover das vendas)")
    forma_pagamento: str | None = Field(default=None, description="avista ou parcelado")
