from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import Member

router = APIRouter(prefix="/members", tags=["Members"])
templates = Jinja2Templates(directory="templates")

@router.get("/list")
def list_members(request: Request, db: Session = Depends(get_db)):
    members = db.query(Member).all()
    return templates.TemplateResponse("members_list.html", {"request": request, "members": members})

# ✅ Show Add Member Form
@router.get("/add")
def add_member_form(request: Request):
    return templates.TemplateResponse("add_member.html", {"request": request})


# ✅ Handle Form Submit
@router.post("/add")
def create_member(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    new_member = Member(name=name, age=age, email=email)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return templates.TemplateResponse("add_member.html", {
        "request": request,
        "message": "✅ Member added successfully!"
    })