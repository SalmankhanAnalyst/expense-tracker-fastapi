import models
from database import get_db
from datetime import date
from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import pandas as pd


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)


@router.get("/by-member/{member_id}", status_code=status.HTTP_200_OK)
def get_expenses_by_member(member_id: int, db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).filter(models.Expense.member_id == member_id).all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "count": len(expenses), "data": [e.__dict__ for e in expenses]}
    )


@router.get("/by-category/{category}", status_code=status.HTTP_200_OK)
def get_expenses_by_category(category: str, db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).filter(models.Expense.category == category).all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "count": len(expenses), "data": [e.__dict__ for e in expenses]}
    )


@router.get("/by-date-range", status_code=status.HTTP_200_OK)
def get_expenses_by_date_range(start_date: date, end_date: date, db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).filter(
        models.Expense.date >= start_date,
        models.Expense.date <= end_date
    ).all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "count": len(expenses), "data": [e.__dict__ for e in expenses]}
    )


@router.get("/summary", status_code=status.HTTP_200_OK)
def get_expense_summary(db: Session = Depends(get_db)):
    total = db.query(func.sum(models.Expense.amount)).scalar() or 0
    category_summary = db.query(
        models.Expense.category, func.sum(models.Expense.amount)
    ).group_by(models.Expense.category).all()

    summary = {cat: amt for cat, amt in category_summary}
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "total_spent": total, "category_summary": summary}
    )


@router.get("/monthly-summary", status_code=status.HTTP_200_OK)
def get_monthly_summary(db: Session = Depends(get_db)):
    monthly = db.query(
        func.strftime("%Y-%m", models.Expense.date).label("month"),
        func.sum(models.Expense.amount)
    ).group_by("month").all()

    result = [{"month": m, "total": t} for m, t in monthly]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "monthly_summary": result}
    )


@router.post("/upload-csv", status_code=status.HTTP_201_CREATED)
def upload_expenses_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file)
    expenses = []
    for _, row in df.iterrows():
        expense = models.Expense(
            title=row["title"],
            amount=row["amount"],
            category=row["category"],
            comment=row.get("comment"),
            member_id=row["member_id"],
            is_external=True,
            external_id=row.get("external_id")
        )
        expenses.append(expense)
    db.add_all(expenses)
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"status": "success", "message": f"{len(expenses)} expenses uploaded successfully"}
    )


@router.get("/export-csv", status_code=status.HTTP_200_OK)
def export_expenses_csv(db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).all()
    df = pd.DataFrame([e.__dict__ for e in expenses])
    df = df.drop(columns=["_sa_instance_state"], errors="ignore")
    file_path = "exported_expenses.csv"
    df.to_csv(file_path, index=False)
    return FileResponse(file_path, media_type="text/csv", filename="expenses.csv")


@router.delete("/delete-all", status_code=status.HTTP_200_OK)
def delete_all_expenses(db: Session = Depends(get_db)):
    count = db.query(models.Expense).delete()
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "deleted_records": count}
    )


@router.delete("/delete-external", status_code=status.HTTP_200_OK)
def delete_external_expenses(db: Session = Depends(get_db)):
    count = db.query(models.Expense).filter(models.Expense.is_external == True).delete()
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "deleted_external_records": count}
    )


@router.get("/search", status_code=status.HTTP_200_OK)
def search_expenses(query: str, db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).join(models.Member).filter(
        or_(
            models.Expense.title.ilike(f"%{query}%"),
            models.Expense.comment.ilike(f"%{query}%"),
            models.Member.name.ilike(f"%{query}%")
        )
    ).all()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "results": [e.__dict__ for e in expenses]}
    )


@router.get("/top-category", status_code=status.HTTP_200_OK)
def get_top_category(db: Session = Depends(get_db)):
    top = db.query(
        models.Expense.category,
        func.sum(models.Expense.amount).label("total")
    ).group_by(models.Expense.category).order_by(func.sum(models.Expense.amount).desc()).first()

    if not top:
        return JSONResponse(status_code=200, content={"message": "No expenses found"})

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "top_category": top.category, "total_spent": top.total}
    )

