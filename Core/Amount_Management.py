from fastapi import FastAPI, status, HTTPException, Path, Body
from fastapi.responses import JSONResponse
from fastapi_swagger import patch_fastapi
from contextlib import asynccontextmanager
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

# ---------------------- Lifespan ---------------------- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan Started")  # Startup
    yield
    print("Lifespan Ended")    # Shutdown

# ---------------------- App Setup ---------------------- #
# Use patch_fastapi to enable offline Swagger docs
app = FastAPI(lifespan=lifespan, docs_url=None, swagger_ui_oauth2_swagger=None)
patch_fastapi(app)

# ---------------------- In-Memory Storage ---------------------- #
expenses_db = {}  # key: id (int), value: expense dict
current_id = 1

# ---------------------- Enum Class ---------------------- #
class PaymentType(str, Enum):
    cash = "cash"
    card = "card"
    crypto = "crypto"

# ---------------------- Pydantic Models ---------------------- #
class ExpenseBase(BaseModel):
    title: str = Field(..., description="Expense title", min_length=3)
    amount: float = Field(..., gt=0, description="Must be positive")
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    payment: PaymentType = Field(..., description="Payment type")

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int

# ---------------------- Helper ---------------------- #
def find_expense_or_404(expense_id: int):
    """Return expense dict if found, otherwise raise 404."""
    expense = expenses_db.get(expense_id)
    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id {expense_id} not found"
        )
    return expense

# ---------------------- API Endpoints ---------------------- #
@app.get("/", status_code=status.HTTP_200_OK)
def root():
    """Root endpoint with a welcome message."""
    return JSONResponse(content={"message": "Expense Management API"}, status_code=status.HTTP_200_OK)

# POST /expenses - Create a new expense
@app.post("/expenses", status_code=status.HTTP_201_CREATED, response_model=ExpenseResponse)
def create_expense(expense: ExpenseCreate = Body()):
    global current_id
    new_id = current_id
    current_id += 1
    expense_dict = {"id": new_id,"title": expense.title.title(), "amount": expense.amount, "description": expense.description, "payment": expense.payment}
    expenses_db[new_id] = expense_dict
    return expense_dict

# GET /expenses - Retrieve all expenses
@app.get("/expenses", status_code=status.HTTP_200_OK, response_model=list[ExpenseResponse])
def get_all_expenses():
    return list(expenses_db.values())

# GET /expenses/{id} - Retrieve a single expense by ID
@app.get("/expenses/{id}", status_code=status.HTTP_200_OK, response_model=ExpenseResponse)
def get_expense_by_id(id: int = Path(..., ge=1, description="Expense ID")):
    expense = find_expense_or_404(id)
    return expense

# PUT /expenses/{id} - Update an existing expense
@app.put("/expenses/{id}", status_code=status.HTTP_200_OK, response_model=ExpenseResponse)
def update_expense(
    id: int = Path(..., ge=1),
    update_data: ExpenseUpdate = Body()
):
    expense = find_expense_or_404(id)
    # Update only provided fields
    if update_data.title is not None:
        expense["title"] = update_data.title
    if update_data.amount is not None:
        expense["amount"] = update_data.amount
    if update_data.description is not None:
        expense["description"] = update_data.description
    if update_data.payment is not None:
        expense["payment"] = update_data.payment
    return expense

# DELETE /expenses/{id} - Delete an expense
@app.delete("/expenses/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(id: int = Path(..., ge=1)):
    expense = find_expense_or_404(id)
    del expenses_db[id]
    # Return no content (204) – no response body
    return