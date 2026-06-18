from enum import Enum
from pydantic import BaseModel
from typing import List

class FormaPagamento(str, Enum):
    AVISTA = "avista"
    PARCELADO = "parcelado"

class Marca(str, Enum):
    AVON = "Avon"
    NATURA = "Natura"
    OBOTICARIO = "O Boticário"
    EUDORA = "Eudora"
    CASA_ESTILO = "Casa Estilo"
    QUEM_DISSE_BERENICE = "Quem Disse, Berenice?"
    OUI = "Oui"

class SaleItem(BaseModel):
    produto: str
    marca: Marca
    quantidade: int

class SaleExtraction(BaseModel):
    cliente: str
    telefone: str | None = None
    itens: List[SaleItem]
    valor_total: float
    forma_pagamento: FormaPagamento
    quantidade_parcelas: int
    custo_total: float
