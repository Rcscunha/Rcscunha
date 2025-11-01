"""Unit tests for the FinanceManager and Transaction classes."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

from finance_app.storage import FinanceManager, Transaction


class FinanceManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_path = Path(self.temp_dir.name) / "finance.json"
        self.manager = FinanceManager(str(self.storage_path))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_expense_creates_file(self) -> None:
        transaction = Transaction.create(
            amount=120.45,
            category="moradia",
            description="Conta de luz",
            entry_date="2024-01-10",
        )
        self.manager.add_transaction("expenses", transaction)

        self.assertTrue(self.storage_path.exists())
        with self.storage_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        self.assertEqual(len(data["expenses"]), 1)
        self.assertEqual(data["expenses"][0]["amount"], 120.45)

    def test_summary_returns_expected_values(self) -> None:
        self.manager.add_transaction(
            "expenses",
            Transaction.create(100, "alimentação", "Supermercado"),
        )
        self.manager.add_transaction(
            "incomes",
            Transaction.create(2500, "salário", "Pagamento mensal"),
        )
        self.manager.add_transaction(
            "investments",
            Transaction.create(500, "renda fixa", "Tesouro Direto"),
        )

        summary = self.manager.summary()
        self.assertEqual(summary["total_expenses"], 100)
        self.assertEqual(summary["total_incomes"], 2500)
        self.assertEqual(summary["total_investments"], 500)
        self.assertEqual(summary["balance"], 2400)

    def test_totals_by_category_groups_values(self) -> None:
        self.manager.add_transaction(
            "expenses",
            Transaction.create(80, "alimentação", "Almoço"),
        )
        self.manager.add_transaction(
            "expenses",
            Transaction.create(120, "alimentação", "Jantar"),
        )
        self.manager.add_transaction(
            "expenses",
            Transaction.create(200, "moradia", "Aluguel"),
        )

        totals = self.manager.totals_by_category("expenses")
        self.assertEqual(totals["alimentação"], 200)
        self.assertEqual(totals["moradia"], 200)

    def test_invalid_date_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            Transaction.create(10, "teste", "teste", entry_date="2024-31-31")


if __name__ == "__main__":
    unittest.main()
