from fastapi import FastAPI, status, HTTPException, Path, Body, Depends
from fastapi.responses import JSONResponse
from fastapi_swagger import patch_fastapi
from contextlib import asynccontextmanager
from Database import Base, engine, get_db, Payment_History
from sqlalchemy.orm import Session
from Schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse

# ---------------------- Lifespan ---------------------- #
# Application startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan Started")  # Startup
    # Create database tables if they do not exist
    Base.metadata.create_all(bind=engine)
    yield
    print("Lifespan Ended")  # Shutdown


# ---------------------- App Setup ---------------------- #
# Use patch_fastapi to enable offline Swagger docs
app = FastAPI(lifespan=lifespan, docs_url=None, swagger_ui_oauth2_swagger=None)
patch_fastapi(app)



# ---------------------- Helper Function Raises 404 Error ---------------------- #
def get_expense_or_404(expense_id: int, db: Session):
    """Get expense by ID or raise 404"""
    # Search expense by ID
    expense = db.query(Payment_History).filter_by(id=expense_id).first()
    # Raise error if not found
    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id {expense_id} not found")
    return expense


# ---------------------- API Endpoints ---------------------- #
# Root endpoint
@app.get("/", status_code=status.HTTP_200_OK)
def root():
    """Root endpoint with a welcome message."""
    return JSONResponse(content={"message": "Expense Management API"}, status_code=status.HTTP_200_OK)


# POST /expenses - Create a new expense
@app.post("/expenses", status_code=status.HTTP_201_CREATED, response_model=ExpenseResponse)
def create_expense(expense: ExpenseCreate = Body(), db: Session = Depends(get_db)):
    # Create SQLAlchemy object
    new_expense = Payment_History(title=expense.title.title(), amount=expense.amount, description=expense.description, payment_type=expense.payment_type)
    # Add object to session & Save changes into database & Refresh
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


# GET /expenses - Retrieve all expenses
@app.get("/expenses", status_code=status.HTTP_200_OK, response_model=list[ExpenseResponse])
def get_all_expenses(db: Session = Depends(get_db)):
    # Retrieve all expense records
    query = db.query(Payment_History).all()
    return list(query)


# GET /expenses/{id} - Retrieve a single expense by ID
@app.get("/expenses/{expense_id}", status_code=status.HTTP_200_OK, response_model=ExpenseResponse)
def get_expense_by_id(expense_id: int = Path(..., ge=1, description="Expense ID"), db: Session = Depends(get_db)):
    # Retrieve expense or raise 404
    expense = get_expense_or_404(expense_id, db)
    return expense


# PUT /expenses/{id} - Update an existing expense
@app.put("/expenses/{expense_id}", status_code=status.HTTP_200_OK, response_model=ExpenseResponse)
def update_expense(expense_id: int = Path(..., ge=1), update_data: ExpenseUpdate = Body(),
                   db: Session = Depends(get_db)):
    # Retrieve expense or raise 404
    expense = get_expense_or_404(expense_id, db)
    # Update fields
    if update_data.title is not None:
        expense.title = update_data.title
    if update_data.amount is not None:
        expense.amount = update_data.amount
    if update_data.description is not None:
        expense.description = update_data.description
    if update_data.payment_type is not None:
        expense.payment_type = update_data.payment_type
    # Save changes into database & Refresh updated object
    db.commit()
    db.refresh(expense)
    return expense


# DELETE /expenses/{id} - Delete an expense
@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    # Retrieve expense or raise 404
    expense = get_expense_or_404(expense_id, db)
    # Delete expense from database & Save changes
    db.delete(expense)
    db.commit()
    return None