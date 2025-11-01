# Finance Tracker CLI

Este projeto fornece um aplicativo de linha de comando simples para monitorar suas finanças pessoais com lançamentos diários de despesas e receitas.

## Funcionalidades

- Registrar transações de **receita** e **despesa** com categoria, descrição e data.
- Listar transações filtrando por período ou limitando a quantidade de registros.
- Gerar um resumo diário com totais de entrada, saída e saldo.

## Requisitos

- Python 3.10 ou superior.
- Nenhuma dependência externa é necessária (usa `sqlite3` da biblioteca padrão). Para executar os testes automatizados é necessário o `pytest`.

## Instalação e uso

1. Crie e ative um ambiente virtual (opcional, mas recomendado).
2. Instale o pacote em modo editável:

   ```bash
   pip install -e .
   ```

   > Se preferir executar diretamente sem instalação, você pode chamar `python -m finance_app` a partir da raiz do projeto.

3. Execute os comandos disponíveis:

   ```bash
   # Registrar uma receita de R$ 100,00 na data de hoje
   python -m finance_app add-income 100 --category salario --description "Pagamento"

   # Registrar uma despesa em uma data específica
   python -m finance_app add-expense 35.5 --date 2024-03-01 --category mercado

   # Listar transações
   python -m finance_app list --start 2024-03-01 --end 2024-03-31

   # Resumo do dia atual
   python -m finance_app summary
   ```

Por padrão o banco de dados é criado em `~/.finance_manager/transactions.db`. Você pode alterar o local com a flag `--database /caminho/para/arquivo.db`.

## Executando os testes

```bash
pytest
```
