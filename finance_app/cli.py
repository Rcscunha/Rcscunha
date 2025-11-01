"""Command line interface for the finance tracking application."""

from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from .database import FinanceRepository, format_transactions


def _parse_date(value: Optional[str]) -> date:
    if value is None:
        return date.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Dates must use the format YYYY-MM-DD"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Track daily expenses and income entries.",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=None,
        help="Optional path to the SQLite database file.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_common = argparse.ArgumentParser(add_help=False)
    add_common.add_argument(
        "amount",
        type=float,
        help="Amount of the transaction (positive number).",
    )
    add_common.add_argument(
        "--date",
        dest="tx_date",
        type=_parse_date,
        default=None,
        help="Date of the transaction (YYYY-MM-DD). Defaults to today.",
    )
    add_common.add_argument(
        "--category",
        default="general",
        help="Category for the transaction.",
    )
    add_common.add_argument(
        "--description",
        default="",
        help="Optional description for the transaction.",
    )

    income_parser = subparsers.add_parser(
        "add-income",
        parents=[add_common],
        help="Register an income transaction.",
    )
    income_parser.set_defaults(tx_type="income")

    expense_parser = subparsers.add_parser(
        "add-expense",
        parents=[add_common],
        help="Register an expense transaction.",
    )
    expense_parser.set_defaults(tx_type="expense")

    list_parser = subparsers.add_parser(
        "list",
        help="List transactions with optional date filters.",
    )
    list_parser.add_argument(
        "--start",
        type=_parse_date,
        default=None,
        help="Start date (inclusive) in YYYY-MM-DD format.",
    )
    list_parser.add_argument(
        "--end",
        type=_parse_date,
        default=None,
        help="End date (inclusive) in YYYY-MM-DD format.",
    )
    list_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of results returned.",
    )

    summary_parser = subparsers.add_parser(
        "summary",
        help="Show a summary for a specific day.",
    )
    summary_parser.add_argument(
        "--date",
        dest="summary_date",
        type=_parse_date,
        default=None,
        help="Target date for the summary (defaults to today).",
    )

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    repo = FinanceRepository(args.database)

    if args.command in {"add-income", "add-expense"}:
        tx_date = args.tx_date or date.today()
        repo.add_transaction(
            tx_date=tx_date,
            amount=args.amount,
            tx_type=args.tx_type,
            category=args.category,
            description=args.description,
        )
        print(
            f"Added {args.tx_type} of {args.amount:.2f} on {tx_date.isoformat()} in {args.category}."
        )
        return 0

    if args.command == "list":
        transactions = repo.list_transactions(
            start_date=args.start,
            end_date=args.end,
            limit=args.limit,
        )
        print(format_transactions(transactions))
        return 0

    if args.command == "summary":
        summary_date = args.summary_date or date.today()
        summary = repo.get_daily_summary(summary_date)
        print(
            "Summary for {date}:\n  Income: {income:.2f}\n  Expense: {expense:.2f}\n  Balance: {balance:.2f}".format(
                date=summary_date.isoformat(),
                income=summary["income"],
                expense=summary["expense"],
                balance=summary["balance"],
            )
        )
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
