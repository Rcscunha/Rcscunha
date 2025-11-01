"""Database layer for the finance tracking application."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Generator, Iterable, List, Optional

DEFAULT_DB_PATH = Path.home() / ".finance_manager" / "transactions.db"


@dataclass
class Transaction:
    """Representation of a single financial transaction."""

    id: int
    date: date
    type: str
    category: str
    description: str
    amount: float


class FinanceRepository:
    """Handles CRUD operations for financial transactions."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        if not self.db_path.parent.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _initialize(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                    category TEXT NOT NULL,
                    description TEXT,
                    amount REAL NOT NULL
                )
                """
            )
            conn.commit()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def add_transaction(
        self,
        *,
        tx_date: date,
        amount: float,
        tx_type: str,
        category: str,
        description: str = "",
    ) -> int:
        if tx_type not in {"income", "expense"}:
            raise ValueError("Transaction type must be 'income' or 'expense'.")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        with self._connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO transactions (date, type, category, description, amount)
                VALUES (?, ?, ?, ?, ?)
                """,
                (tx_date.isoformat(), tx_type, category, description, amount),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def list_transactions(
        self,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = None,
    ) -> List[Transaction]:
        query = "SELECT id, date, type, category, description, amount FROM transactions"
        clauses: List[str] = []
        params: List[str] = []

        if start_date:
            clauses.append("date >= ?")
            params.append(start_date.isoformat())
        if end_date:
            clauses.append("date <= ?")
            params.append(end_date.isoformat())

        if clauses:
            query += " WHERE " + " AND ".join(clauses)

        query += " ORDER BY date DESC, id DESC"
        if limit:
            query += " LIMIT ?"
            params.append(str(limit))

        with self._connection() as conn:
            rows = conn.execute(query, params).fetchall()

        return [
            Transaction(
                id=row[0],
                date=date.fromisoformat(row[1]),
                type=row[2],
                category=row[3],
                description=row[4] or "",
                amount=float(row[5]),
            )
            for row in rows
        ]

    def get_daily_summary(self, target_date: date) -> dict:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT type, SUM(amount) FROM transactions
                WHERE date = ?
                GROUP BY type
                """,
                (target_date.isoformat(),),
            ).fetchall()

        summary = {"income": 0.0, "expense": 0.0}
        for tx_type, total in rows:
            summary[tx_type] = float(total or 0.0)

        summary["balance"] = summary["income"] - summary["expense"]
        return summary

    def get_overview(self) -> dict:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT date, type, SUM(amount) as total
                FROM transactions
                GROUP BY date, type
                ORDER BY date ASC
                """
            ).fetchall()

        overview = {}
        for tx_date, tx_type, total in rows:
            day = date.fromisoformat(tx_date)
            if day not in overview:
                overview[day] = {"income": 0.0, "expense": 0.0}
            overview[day][tx_type] = float(total or 0.0)

        return overview


def format_transactions(transactions: Iterable[Transaction]) -> str:
    """Return a human-readable table for the given transactions."""

    if not transactions:
        return "No transactions found."

    headers = ["Date", "Type", "Category", "Description", "Amount"]
    rows = []
    for tx in transactions:
        rows.append(
            [
                tx.date.isoformat(),
                tx.type,
                tx.category,
                tx.description,
                f"{tx.amount:,.2f}",
            ]
        )

    col_widths = [max(len(str(cell)) for cell in column) for column in zip(headers, *rows)]

    def _format_row(row: Iterable[str]) -> str:
        return " | ".join(str(cell).ljust(width) for cell, width in zip(row, col_widths))

    separator = "-+-".join("-" * width for width in col_widths)
    output_lines = [_format_row(headers), separator]
    output_lines.extend(_format_row(row) for row in rows)
    return "\n".join(output_lines)
