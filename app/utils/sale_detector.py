SALE_HINTS = [
    "comprou",
    "vendeu",
    "parcela",
    "parcelado",
    "pix",
    "avista",
    "à vista",
    "custo",
    "cliente",
    "natura",
    "avon",
    "oboticario",
    "o boticário",
    "produto",
    "pagou",
    "venda",
    "cancelar",
    "pagou",
    "parcela"
]


def may_be_sale(text: str) -> bool:

    text = text.lower()

    return any(
        keyword in text
        for keyword in SALE_HINTS
    )


def is_valid_sale(sale) -> bool:

    if not sale.cliente:
        return False

    if not sale.produto:
        return False

    if sale.valor_total <= 0:
        return False

    if sale.quantidade <= 0:
        return False

    return True