from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter

from src.schemas.expense_schema import ExpenseCreate, ExpenseResponse, TotalResponse
from src.services import expense_service

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse, status_code=201)
def create_expense(payload: ExpenseCreate) -> ExpenseResponse:
    """Create a new expense entry."""
    return expense_service.create_expense(payload)


@router.get("", response_model=List[ExpenseResponse])
def list_expenses(category: Optional[str] = None) -> List[ExpenseResponse]:
    """
    Return all expenses.
    Optionally filter by category using ?category=<name>.
    """
    return expense_service.get_expenses(category=category)


@router.get("/total", response_model=TotalResponse)
def total_expenses(category: Optional[str] = None) -> TotalResponse:
    """
    Return the sum of all expense amounts.
    Optionally filter by category using ?category=<name>.
    """
    return expense_service.get_total(category=category)


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: str) -> None:
    """Delete an expense by its UUID."""
    expense_service.delete_expense(expense_id)
