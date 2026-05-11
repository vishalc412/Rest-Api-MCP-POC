from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.health import HealthExpense, ExpenseCategory

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/")
async def list_expenses(
    start_date: date | None = None,
    end_date: date | None = None,
    category: ExpenseCategory | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(HealthExpense).where(HealthExpense.user_id == current_user.id)
    if start_date:
        query = query.where(HealthExpense.expense_date >= start_date)
    if end_date:
        query = query.where(HealthExpense.expense_date <= end_date)
    if category:
        query = query.where(HealthExpense.category == category)

    result = await db.execute(query.order_by(HealthExpense.expense_date.desc()))
    expenses = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "amount": float(e.amount) if e.amount else 0,
            "category": e.category,
            "expense_date": e.expense_date,
            "vendor_name": e.vendor_name,
        }
        for e in expenses
    ]


@router.get("/summary")
async def expense_summary(
    year: int | None = None,
    month: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(
        HealthExpense.category,
        func.sum(HealthExpense.amount).label("total"),
        func.count(HealthExpense.id).label("count"),
    ).where(HealthExpense.user_id == current_user.id)

    if year:
        query = query.where(extract("year", HealthExpense.expense_date) == year)
    if month:
        query = query.where(extract("month", HealthExpense.expense_date) == month)

    query = query.group_by(HealthExpense.category)
    result = await db.execute(query)
    rows = result.all()

    return {
        "breakdown": [
            {"category": r.category, "total": float(r.total or 0), "count": r.count}
            for r in rows
        ],
        "grand_total": sum(float(r.total or 0) for r in rows),
    }
