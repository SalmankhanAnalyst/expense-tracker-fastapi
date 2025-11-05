from pydantic import BaseModel
from datetime import date
from typing import Optional

# Member schemas
class MemberBase(BaseModel):
    name: str
    age: Optional[int] = None
    email: str

class MemberCreate(MemberBase):
    pass

class MemberResponse(MemberBase):
    id: int
    class Config:
        orm_mode = True


# Expense schemas

class ExpenseBase(BaseModel):
    title: str
    categories: str
    amount: float
    date: date
    comment: Optional[str] = None
    is_external: bool = False
    external_id: Optional[int] = None
    member_id: int

class ExpenseCreate(ExpenseBase):
    title: str
    category: str
    amount: float
    date: date
    comment: str | None = None
    member_id: int

class ExpenseResponse(ExpenseBase):
    id: int
    class Config:
        orm_mode = True
