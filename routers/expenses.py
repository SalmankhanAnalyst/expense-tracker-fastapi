from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from fastapi.templating import Jinja2Templates
from fastapi import Request

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)

templates = Jinja2Templates(directory="templates")


# ✅ List all expenses
@router.get("/list", response_class=HTMLResponse)
def list_expenses(request: Request, db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).all()
    return templates.TemplateResponse("expense_list.html", {"request": request, "expenses": expenses})


# ✅ Show form to create a new expense
@router.get("/add", response_class=HTMLResponse)
def add_expense_form(request: Request, db: Session = Depends(get_db)):
    members = db.query(models.Member).all()
    return templates.TemplateResponse("expense_add.html", {"request": request, "members": members})


# ✅ Create expense (POST)
@router.post("/add")
def create_expense(
    title: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...),
    date: str = Form(...),
    comment: str = Form(None),
    member_id: int = Form(...),
    db: Session = Depends(get_db)
):
    expense = models.Expense(
        title=title,
        category=category,
        amount=amount,
        date=date,
        comment=comment,
        member_id=member_id,
    )
    db.add(expense)
    db.commit()

    return RedirectResponse(url="/expenses/list", status_code=303)


# ✅ Get expense by ID (HTML UI)
@router.get("/view/{id}", response_class=HTMLResponse)
def view_expense(id: int, request: Request, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.id == id).first()
    if not expense:
        raise HTTPException(404, "Expense not found")

    return templates.TemplateResponse("expense_view.html", {"request": request, "expense": expense})


# ✅ Delete expense
@router.get("/delete/{id}")
def delete_expense(id: int, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.id == id).first()
    if not expense:
        raise HTTPException(404, "Expense not found")

    db.delete(expense)
    db.commit()
    return RedirectResponse(url="/expenses/list", status_code=303)
