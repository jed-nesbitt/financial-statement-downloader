from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re

import pandas as pd
import yfinance as yf


def safe_folder_name(s: str) -> str:
    # folder-safe: "CBA.AX" -> "CBA_AX"
    s = s.strip().replace(".", "_")
    s = re.sub(r"[^A-Za-z0-9_\-]+", "_", s)
    return s


def clean_statement_no_transpose(df: pd.DataFrame, statement_name: str) -> pd.DataFrame:
    """
    Keeps rows = line items, columns = dates.
    Adds a 'statement' column and resets index for clean CSV output.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    clean = df.copy()
    clean.columns = [str(c) for c in clean.columns]  # nicer CSV headers
    clean = clean.reset_index().rename(columns={"index": "line_item"})
    clean.insert(1, "statement", statement_name)
    return clean


def save_csv(df: pd.DataFrame, path: Path) -> None:
    if df is None or df.empty:
        print(f"[WARN] Not saved (empty): {path.name}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")  # Excel-friendly
    print(f"[OK] Saved: {path.as_posix()}")


def main() -> None:
    ticker_input = input("Enter a ticker (e.g. CBA.AX, WBC.AX, AAPL): ").strip().upper()
    if not ticker_input:
        print("No ticker entered. Exiting.")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ticker_folder = safe_folder_name(ticker_input)

    out_dir = Path("outputs") / ts / ticker_folder  # ✅ outputs/timestamp/ticker/

    t = yf.Ticker(ticker_input)

    income_statement = t.financials
    balance_sheet = t.balance_sheet
    cash_flow = t.cashflow

    clean_income = clean_statement_no_transpose(income_statement, "income")
    clean_balance = clean_statement_no_transpose(balance_sheet, "balance_sheet")
    clean_cash = clean_statement_no_transpose(cash_flow, "cash_flow")

    save_csv(clean_income, out_dir / "income_statement.csv")
    save_csv(clean_balance, out_dir / "balance_sheet.csv")
    save_csv(clean_cash, out_dir / "cash_flow.csv")


if __name__ == "__main__":
    main()
