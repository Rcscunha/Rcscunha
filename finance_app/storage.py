"""Utilities for persisting finance data to a JSON file."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
import json
from pathlib import Path
from typing import Dict, List, Literal, Optional
import uuid


TransactionType = Literal["expenses", "incomes", "investments"]


@dataclass
class Transaction:
    """Represents a generic financial transaction."""

    id: str
    amount: float
    category: str
    description: str
    entry_date: str
    metadata: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        amount: float,
        category: str,
        description: str,
        entry_date: Optional[str] = None,
        **metadata: str,
    ) -> "Transaction":
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if entry_date is None:
            entry_date = date.today().isoformat()
        else:
            _validate_date(entry_date)

        return cls(
            id=str(uuid.uuid4()),
            amount=round(float(amount), 2),
            category=category.strip() or "general",
            description=description.strip(),
            entry_date=entry_date,
            metadata={k: v for k, v in metadata.items() if v is not None},
        )


class FinanceManager:
    """Handles persistence and retrieval of financial data."""

    def __init__(self, storage_path: str = "finance_data.json") -> None:
        self.path = Path(storage_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> Dict[TransactionType, List[Dict[str, object]]]:
        if not self.path.exists():
            return {"expenses": [], "incomes": [], "investments": []}

        with self.path.open("r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid JSON data in storage file.") from exc

        for key in ("expenses", "incomes", "investments"):
            data.setdefault(key, [])

        return data

    def _save(self) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(self._data, file, indent=2, ensure_ascii=False)

    def add_transaction(self, transaction_type: TransactionType, transaction: Transaction) -> None:
        self._data[transaction_type].append(asdict(transaction))
        self._save()

    def list_transactions(self, transaction_type: Optional[TransactionType] = None) -> Dict[str, List[Dict[str, object]]]:
        if transaction_type:
            return {transaction_type: list(self._data[transaction_type])}
        return {k: list(v) for k, v in self._data.items()}

    def summary(self) -> Dict[str, float]:
        total_expenses = sum(item["amount"] for item in self._data["expenses"])
        total_incomes = sum(item["amount"] for item in self._data["incomes"])
        total_investments = sum(item["amount"] for item in self._data["investments"])
        return {
            "total_expenses": round(total_expenses, 2),
            "total_incomes": round(total_incomes, 2),
            "total_investments": round(total_investments, 2),
            "balance": round(total_incomes - total_expenses, 2),
        }

    def totals_by_category(self, transaction_type: TransactionType) -> Dict[str, float]:
        totals: Dict[str, float] = {}
        for item in self._data[transaction_type]:
            category = item.get("category", "general")
            totals[category] = round(totals.get(category, 0.0) + float(item["amount"]), 2)
        return totals


def _validate_date(date_string: str) -> None:
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(
            "Dates must be formatted as YYYY-MM-DD."
        ) from exc
