from fastapi import FastAPI, status, HTTPException, Path, Body, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_swagger import patch_fastapi
from contextlib import asynccontextmanager
from Core.Database import Base, engine, get_db
from sqlalchemy.orm import Session
from Core.Schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from Core.i18n import detect_language, get_translations

from Users.Models import UserModel
from Expenses.Models import Payment_History

from Auth.router import router as auth_router
from Auth.deps import get_current_user


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

app.include_router(auth_router)


# ---------------------- Helper Function Raises 404 Error ---------------------- #
def get_expense_or_404(expense_id: int, db: Session):
    """Get expense by ID or raise 404"""
    # Search expense by ID
    expense = db.query(Payment_History).filter_by(id=expense_id).first()
    # Raise error if not found
    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="expense_not_found"
        )
    return expense


# ---------------------- API Endpoints ---------------------- #
# Root endpoint
@app.get("/api", status_code=status.HTTP_200_OK)
def root(request: Request):
    """Root endpoint with a welcome message."""
    lang = detect_language(request)
    t = get_translations(lang)
    return JSONResponse(
        content={"message": t.gettext("welcome_message")},
        status_code=status.HTTP_200_OK,
    )


# POST /expenses - Create a new expense
@app.post(
    "/expenses", status_code=status.HTTP_201_CREATED, response_model=ExpenseResponse
)
def create_expense(
    request: Request,
    expense: ExpenseCreate = Body(),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    new_expense = Payment_History(
        title=expense.title.title(),
        amount=expense.amount,
        description=expense.description,
        payment_type=expense.payment_type,
        user_id=current_user.id,
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


# GET /expenses - Retrieve all expenses
@app.get(
    "/expenses", status_code=status.HTTP_200_OK, response_model=list[ExpenseResponse]
)
def get_all_expenses(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    query = db.query(Payment_History).filter_by(user_id=current_user.id).all()
    return list(query)


# GET /expenses/{id} - Retrieve a single expense by ID
@app.get(
    "/expenses/{expense_id}",
    status_code=status.HTTP_200_OK,
    response_model=ExpenseResponse,
)
def get_expense_by_id(
    expense_id: int = Path(..., ge=1, description="Expense ID"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    expense = get_expense_or_404(expense_id, db)
    if expense.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="expense_not_found"
        )
    return expense


# PUT /expenses/{id} - Update an existing expense
@app.put(
    "/expenses/{expense_id}",
    status_code=status.HTTP_200_OK,
    response_model=ExpenseResponse,
)
def update_expense(
    expense_id: int = Path(..., ge=1),
    update_data: ExpenseUpdate = Body(),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    expense = get_expense_or_404(expense_id, db)
    if expense.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="expense_not_found"
        )
    if update_data.title is not None:
        expense.title = update_data.title
    if update_data.amount is not None:
        expense.amount = update_data.amount
    if update_data.description is not None:
        expense.description = update_data.description
    if update_data.payment_type is not None:
        expense.payment_type = update_data.payment_type
    db.commit()
    db.refresh(expense)
    return expense


# DELETE /expenses/{id} - Delete an expense
@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    expense = get_expense_or_404(expense_id, db)
    if expense.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="expense_not_found"
        )
    db.delete(expense)
    db.commit()
    return None
