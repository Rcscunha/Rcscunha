from datetime import date
from pathlib import Path

import pytest

from finance_app.database import FinanceRepository, format_transactions


@pytest.fixture()
def temp_db(tmp_path: Path) -> Path:
    return tmp_path / "finance.db"


def test_add_and_list_transactions(temp_db: Path) -> None:
    repo = FinanceRepository(temp_db)
    repo.add_transaction(
        tx_date=date(2023, 12, 31),
        amount=100.0,
        tx_type="income",
        category="salary",
        description="December salary",
    )
    repo.add_transaction(
        tx_date=date(2024, 1, 1),
        amount=40.0,
        tx_type="expense",
        category="groceries",
        description="Weekly shopping",
    )

    transactions = repo.list_transactions()
    assert len(transactions) == 2
    assert transactions[0].category == "groceries"
    assert transactions[1].category == "salary"


def test_get_daily_summary(temp_db: Path) -> None:
    repo = FinanceRepository(temp_db)
    repo.add_transaction(
        tx_date=date(2024, 2, 1),
        amount=150.0,
        tx_type="income",
        category="freelance",
    )
    repo.add_transaction(
        tx_date=date(2024, 2, 1),
        amount=50.0,
        tx_type="expense",
        category="transport",
    )

    summary = repo.get_daily_summary(date(2024, 2, 1))
    assert summary == {"income": 150.0, "expense": 50.0, "balance": 100.0}


def test_format_transactions_table(temp_db: Path) -> None:
    repo = FinanceRepository(temp_db)
    repo.add_transaction(
        tx_date=date(2024, 3, 1),
        amount=200.0,
        tx_type="income",
        category="bonus",
        description="Performance bonus",
    )

    table = format_transactions(repo.list_transactions())
    assert "Date" in table
    assert "bonus" in table
    assert "200.00" in table


def test_reject_invalid_type(temp_db: Path) -> None:
    repo = FinanceRepository(temp_db)
    with pytest.raises(ValueError):
        repo.add_transaction(
            tx_date=date.today(),
            amount=10.0,
            tx_type="transfer",
            category="other",
        )


def test_reject_non_positive_amount(temp_db: Path) -> None:
    repo = FinanceRepository(temp_db)
    with pytest.raises(ValueError):
        repo.add_transaction(
            tx_date=date.today(),
            amount=0,
            tx_type="expense",
            category="other",
        )
