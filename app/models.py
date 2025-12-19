from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, model_validator


class AssignmentRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assignment_id: str
    client_id: str
    client_name: str
    billing_email: Optional[str]
    assignment_type: str
    completed_at: str
    status: str
    default_credits: float
    default_credit_value_usd: int
    currency: str
    credits_override: Optional[float] = None
    credit_value_override_usd: Optional[int] = None


class InvoiceLineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str
    assignment_type: str
    quantity: int
    credits_per_assignment: float
    line_credits: float
    unit_credit_value_usd: int
    line_amount_usd: int


class Invoice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    invoice_id: str
    client_id: str
    client_name: str
    billing_month: str
    currency: str
    line_items: List[InvoiceLineItem]
    total_credits: float
    total_amount_usd: int
    generated_at: str

    @model_validator(mode="after")
    def check_totals(self) -> "Invoice":
        credits_sum = sum(Decimal(str(item.line_credits)) for item in self.line_items)
        amount_sum = sum(Decimal(item.line_amount_usd) for item in self.line_items)
        if credits_sum and abs(credits_sum - Decimal(str(self.total_credits))) > Decimal("0.0001"):
            raise ValueError("total_credits does not match line items")
        if amount_sum and int(amount_sum) != int(self.total_amount_usd):
            raise ValueError("total_amount_usd does not match line items")
        return self
