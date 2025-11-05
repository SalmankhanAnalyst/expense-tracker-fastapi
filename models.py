from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Member(Base):
    __tablename__ = "member"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    email = Column(String(150), nullable=False, unique=True)

    # ✅ Cascade delete (delete expenses when member is deleted)
    expenses = relationship("Expense", back_populates="member", cascade="all, delete")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)        # ✅ length added
    category = Column(String(100), nullable=False)     # ✅ length added
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    comment = Column(String(255))                      # ✅ length added

    member_id = Column(Integer, ForeignKey("member.id", ondelete="CASCADE"))

    member = relationship("Member", back_populates="expenses")
