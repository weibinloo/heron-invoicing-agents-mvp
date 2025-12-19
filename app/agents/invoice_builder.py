from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

from app.models import AssignmentRow, Invoice, InvoiceLineItem


@dataclass
class InvoicePackage:
    invoice: Invoice


class InvoiceBuilderAgent:
    def __init__(self) -> None:
        self._quant = Decimal("0.01")

    def build_invoices(
        self,
        assignments: Iterable[AssignmentRow],
        billing_month: str,
    ) -> list[InvoicePackage]:
        grouped: dict[str, list[AssignmentRow]] = {}
        for row in assignments:
            grouped.setdefault(row.client_id, []).append(row)

        invoices: list[InvoicePackage] = []
        for client_id, rows in grouped.items():
            client_name = rows[0].client_name
            currency = rows[0].currency
            line_items = []

            per_type: dict[str, list[AssignmentRow]] = {}
            for row in rows:
                per_type.setdefault(row.assignment_type, []).append(row)

            for assignment_type, items in per_type.items():
                quantity = len(items)
                credits_override = items[0].credits_override
                credit_value_override = items[0].credit_value_override_usd

                credits_per_assignment = (
                    Decimal(str(credits_override))
                    if credits_override is not None
                    else Decimal(str(items[0].default_credits))
                )
                unit_credit_value = (
                    int(credit_value_override)
                    if credit_value_override is not None
                    else int(items[0].default_credit_value_usd)
                )
                line_credits = (credits_per_assignment * quantity).quantize(
                    self._quant, rounding=ROUND_HALF_UP
                )
                line_amount = (
                    (line_credits * Decimal(unit_credit_value))
                    .quantize(Decimal("1"), rounding=ROUND_HALF_UP)
                )

                line_items.append(
                    InvoiceLineItem(
                        description=f"{assignment_type} ({quantity} completed)",
                        assignment_type=assignment_type,
                        quantity=quantity,
                        credits_per_assignment=float(credits_per_assignment),
                        line_credits=float(line_credits),
                        unit_credit_value_usd=unit_credit_value,
                        line_amount_usd=int(line_amount),
                    )
                )

            total_credits = sum(Decimal(str(item.line_credits)) for item in line_items).quantize(
                self._quant, rounding=ROUND_HALF_UP
            )
            total_amount = sum(Decimal(item.line_amount_usd) for item in line_items)

            invoice = Invoice(
                invoice_id=f"{client_id}-{billing_month}",
                client_id=client_id,
                client_name=client_name,
                billing_month=billing_month,
                currency=currency,
                line_items=line_items,
                total_credits=float(total_credits),
                total_amount_usd=int(total_amount),
                generated_at=datetime.utcnow().isoformat(timespec="seconds") + "Z",
            )
            invoices.append(InvoicePackage(invoice=invoice))

        return invoices
