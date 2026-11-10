"""Read inputs without silently filling, clipping or discarding observations."""
from pathlib import Path
import numpy as np
import pandas as pd


def prepare_data(frame):
    df = frame.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    if df.columns.duplicated().any():
        raise ValueError("Duplicate column names after normalization")
    if not {"date", "gold", "tips"}.issubset(df.columns):
        raise ValueError("Required columns: date, gold, tips")
    if df.empty:
        raise ValueError("Dataset is empty")
    # Excel serial dates require an explicit origin; never guess their unit.
    if pd.api.types.is_numeric_dtype(df.date):
        raise ValueError("Date must contain Excel date cells or ISO date strings, not serial numbers")
    df["date"] = pd.to_datetime(df.date, errors="raise")
    if df.date.isna().any() or (df.date != df.date.dt.normalize()).any():
        raise ValueError("Dates must be nonmissing daily dates without time components")
    if df.date.duplicated().any():
        raise ValueError("Duplicate dates are not allowed")
    for col in ("gold", "tips"):
        df[col] = pd.to_numeric(df[col], errors="raise")
        if np.isinf(df[col]).any():
            raise ValueError(f"Infinite values in {col}")
    if (df.gold.dropna() <= 0).any():
        raise ValueError("Observed gold prices must be positive")
    df = df.sort_values("date", kind="stable").set_index("date")
    df["LOG_GOLD"] = np.log(df.gold)
    # Difference BEFORE any regression-specific missing-value exclusion.
    df["DLGOLD"] = 100 * df.LOG_GOLD.diff()
    df["DTIPS"] = df.tips.diff()
    return df


def load_and_prepare_data(path, sheet_name="aligned_clean_model_ready"):
    return prepare_data(pd.read_excel(Path(path), sheet_name=sheet_name))
