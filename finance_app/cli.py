"""Command line interface for the finance manager."""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict

from .storage import FinanceManager, Transaction


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gerencie despesas, receitas e investimentos usando um arquivo local.",
    )
    parser.add_argument(
        "--storage",
        default="finance_data.json",
        help="Caminho do arquivo JSON onde os lançamentos serão armazenados.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_expense = subparsers.add_parser("add-expense", help="Registrar uma nova despesa.")
    _add_transaction_arguments(add_expense)

    add_income = subparsers.add_parser("add-income", help="Registrar uma nova receita.")
    _add_transaction_arguments(add_income)

    add_investment = subparsers.add_parser(
        "add-investment", help="Registrar um novo investimento."
    )
    _add_transaction_arguments(add_investment)
    add_investment.add_argument(
        "--broker",
        default="",
        help="Corretora ou instituição do investimento.",
    )
    add_investment.add_argument(
        "--return-rate",
        type=str,
        default="",
        help="Taxa de retorno esperada (por exemplo, 12% a.a.).",
    )

    list_parser = subparsers.add_parser(
        "list", help="Listar lançamentos. Use --type para filtrar por categoria."
    )
    list_parser.add_argument(
        "--type",
        choices=["expenses", "incomes", "investments", "all"],
        default="all",
        help="Tipo de lançamento que será exibido.",
    )

    subparsers.add_parser("summary", help="Exibe um resumo financeiro consolidado.")

    totals_parser = subparsers.add_parser(
        "category-totals",
        help="Mostra os totais agrupados por categoria para o tipo escolhido.",
    )
    totals_parser.add_argument(
        "type",
        choices=["expenses", "incomes", "investments"],
        help="Tipo de lançamento que será agrupado.",
    )

    return parser


def _add_transaction_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("amount", type=float, help="Valor do lançamento.")
    subparser.add_argument("category", help="Categoria do lançamento (ex: moradia, salário).")
    subparser.add_argument("description", help="Descrição breve do lançamento.")
    subparser.add_argument(
        "--date",
        dest="entry_date",
        default=None,
        help="Data do lançamento no formato YYYY-MM-DD. Padrão: hoje.",
    )


def _format_output(data: Dict[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def main(argv: list[str] | None = None) -> str:
    parser = _build_parser()
    args = parser.parse_args(argv)

    manager = FinanceManager(storage_path=args.storage)

    if args.command in {"add-expense", "add-income", "add-investment"}:
        transaction_type = {
            "add-expense": "expenses",
            "add-income": "incomes",
            "add-investment": "investments",
        }[args.command]

        metadata: Dict[str, Any] = {}
        if transaction_type == "investments":
            metadata["broker"] = args.broker
            metadata["return_rate"] = args.return_rate

        transaction = Transaction.create(
            amount=args.amount,
            category=args.category,
            description=args.description,
            entry_date=args.entry_date,
            **metadata,
        )
        manager.add_transaction(transaction_type, transaction)
        result = {
            "message": "Lançamento registrado com sucesso.",
            "transaction": transaction.__dict__,
            "type": transaction_type,
        }
        output = _format_output(result)
        print(output)
        return output

    if args.command == "list":
        transaction_type = None if args.type == "all" else args.type
        result = manager.list_transactions(transaction_type)
        output = _format_output(result)
        print(output)
        return output

    if args.command == "summary":
        result = manager.summary()
        output = _format_output(result)
        print(output)
        return output

    if args.command == "category-totals":
        result = manager.totals_by_category(args.type)
        output = _format_output(result)
        print(output)
        return output

    parser.error("Comando desconhecido.")
    return ""


if __name__ == "__main__":  # pragma: no cover - entry point
    main()
