from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


# ---------------------- Enum Class ---------------------- #
# Restrict payment type values
class PaymentType(str, Enum):
    cash = "cash"
    card = "card"
    crypto = "crypto"


# ---------------------- Pydantic Models ---------------------- #
# Base schema used for create, update and response
class ExpenseBase(BaseModel):
    title: str = Field(..., description="Expense title", min_length=3)
    amount: float = Field(..., gt=0, description="Must be positive")
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    payment_type: PaymentType = Field(..., description="Payment type")


# Schema for creating expenses
class ExpenseCreate(ExpenseBase):
    pass


# Schema for updating expenses
class ExpenseUpdate(ExpenseBase):
    pass


# Schema returned to the client
class ExpenseResponse(ExpenseBase):
    id: int
