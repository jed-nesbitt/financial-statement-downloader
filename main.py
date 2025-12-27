from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re
import json
import platform
import sys
import time

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


def save_csv(df: pd.DataFrame, path: Path) -> bool:
    """Save df to CSV. Returns True if saved, False if empty."""
    if df is None or df.empty:
        print(f"[WARN] Not saved (empty): {path.name}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")  # Excel-friendly
    print(f"[OK] Saved: {path.as_posix()}")
    return True


def df_summary(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {"empty": True, "rows": 0, "cols": 0, "columns": []}
    return {
        "empty": False,
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "columns": [str(c) for c in df.columns],
    }


def _json_default(obj):
    """Best-effort JSON serializer for odd types (Path, numpy scalars, timestamps)."""
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    # numpy scalar support without importing numpy
    if hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:
            pass
    return str(obj)


def write_run_metadata(path: Path, meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False, default=_json_default)
    print(f"[OK] Saved: {path.as_posix()}")


def main() -> None:
    start_perf = time.perf_counter()
    run_started = datetime.now().astimezone().isoformat()

    ticker_input = input("Enter a ticker (e.g. CBA.AX, WBC.AX, AAPL): ").strip().upper()
    if not ticker_input:
        print("No ticker entered. Exiting.")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ticker_folder = safe_folder_name(ticker_input)

    out_dir = Path("outputs") / ts / ticker_folder  # outputs/timestamp/ticker/
    out_dir.mkdir(parents=True, exist_ok=True)

    t = yf.Ticker(ticker_input)

    # Pull financial statements
    income_statement = t.financials
    balance_sheet = t.balance_sheet
    cash_flow = t.cashflow

    # Clean for export
    clean_income = clean_statement_no_transpose(income_statement, "income")
    clean_balance = clean_statement_no_transpose(balance_sheet, "balance_sheet")
    clean_cash = clean_statement_no_transpose(cash_flow, "cash_flow")

    # Save CSVs + build a manifest
    outputs: dict[str, dict] = {}

    p_income = out_dir / "income_statement.csv"
    saved_income = save_csv(clean_income, p_income)
    outputs["income_statement"] = {
        "saved": saved_income,
        "path": str(p_income.as_posix()),
        "summary": df_summary(clean_income),
    }

    p_balance = out_dir / "balance_sheet.csv"
    saved_balance = save_csv(clean_balance, p_balance)
    outputs["balance_sheet"] = {
        "saved": saved_balance,
        "path": str(p_balance.as_posix()),
        "summary": df_summary(clean_balance),
    }

    p_cash = out_dir / "cash_flow.csv"
    saved_cash = save_csv(clean_cash, p_cash)
    outputs["cash_flow"] = {
        "saved": saved_cash,
        "path": str(p_cash.as_posix()),
        "summary": df_summary(clean_cash),
    }

    # Optional: grab a few "fast_info" fields (safe + lightweight)
    fast_info_selected = {}
    try:
        fi = getattr(t, "fast_info", None)
        if fi is not None:
            # fast_info behaves like a mapping; pick common keys if present
            for k in ["currency", "exchange", "quoteType", "marketCap", "lastPrice", "previousClose", "timezone"]:
                try:
                    v = fi.get(k) if hasattr(fi, "get") else fi[k]
                    fast_info_selected[k] = v
                except Exception:
                    pass
    except Exception:
        pass

    run_ended = datetime.now().astimezone().isoformat()
    duration_sec = float(time.perf_counter() - start_perf)

    run_metadata = {
        "run_started": run_started,
        "run_ended": run_ended,
        "duration_sec": round(duration_sec, 6),
        "ticker": ticker_input,
        "ticker_folder": ticker_folder,
        "output_dir": str(out_dir.as_posix()),
        "generated_files": outputs,
        "yfinance_fast_info": fast_info_selected,
        "versions": {
            "python": sys.version.split()[0],
            "pandas": getattr(pd, "__version__", "unknown"),
            "yfinance": getattr(yf, "__version__", "unknown"),
        },
        "platform": platform.platform(),
    }

    write_run_metadata(out_dir / "run_metadata.json", run_metadata)


if __name__ == "__main__":
    main()
