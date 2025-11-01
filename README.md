# Finance App CLI

Aplicativo em linha de comando para registrar despesas, receitas e investimentos
utilizando um arquivo JSON local. A ferramenta ajuda a manter o controle das
finanças pessoais e acompanhar o total investido.

## Requisitos

- Python 3.10 ou superior

## Instalação

Clone o repositório e, opcionalmente, crie um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # No Windows use `.venv\\Scripts\\activate`
```

## Como usar

Execute o módulo de linha de comando diretamente com Python:

```bash
python -m finance_app.cli --help
```

Alguns exemplos de comandos:

```bash
# Registrar uma despesa
python -m finance_app.cli add-expense 75.40 alimentacao "Almoço"

# Registrar uma receita
python -m finance_app.cli add-income 2500 salario "Pagamento mensal"

# Registrar um investimento
python -m finance_app.cli add-investment 500 renda_fixa "Tesouro Direto" --broker "Tesouro" --return-rate "12% a.a."

# Listar todos os lançamentos
python -m finance_app.cli list

# Ver resumo financeiro
python -m finance_app.cli summary

# Totais de despesas por categoria
python -m finance_app.cli category-totals expenses
```

Os dados serão salvos por padrão em `finance_data.json`, mas você pode alterar o
arquivo com o parâmetro `--storage`.

## Testes

Para executar os testes unitários:

```bash
python -m unittest discover -s tests
```
