"""Loading and validating uploaded files. No Streamlit code here, so it is easy to test."""
import io
import warnings
import pandas as pd

SUPPORTED = (".csv", ".xlsx", ".xls")


class DataLoadError(Exception):
    """Raised with a friendly message when a file cannot be loaded."""


def get_extension(filename: str) -> str:
    return "." + filename.lower().rsplit(".", 1)[-1] if "." in filename else ""


def list_sheets(file_bytes: bytes) -> list:
    """Return worksheet names of an Excel file."""
    try:
        return pd.ExcelFile(io.BytesIO(file_bytes)).sheet_names
    except Exception as exc:
        raise DataLoadError(f"Could not read the Excel file: {exc}")


def load_dataframe(file_bytes: bytes, filename: str, sheet_name=None) -> pd.DataFrame:
    """Read CSV/Excel bytes into a DataFrame, or raise DataLoadError."""
    ext = get_extension(filename)
    if ext not in SUPPORTED:
        raise DataLoadError(f"Unsupported file type '{ext or 'unknown'}'. Please upload a CSV or Excel file.")
    if not file_bytes:
        raise DataLoadError("The uploaded file is empty.")
    try:
        if ext == ".csv":
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name or 0)
    except pd.errors.EmptyDataError:
        raise DataLoadError("The file has no data.")
    except Exception as exc:
        raise DataLoadError(f"Could not read the file: {exc}")
    if df.empty or df.shape[1] == 0:
        raise DataLoadError("The file was read, but it contains no rows or columns.")
    return try_parse_dates(df)


def try_parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert text columns to dates when most values look like dates."""
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
            continue
        non_null = df[col].dropna()
        if non_null.empty:
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # pandas warns when it guesses date formats
            parsed = pd.to_datetime(non_null.astype(str), errors="coerce")
        if parsed.notna().mean() >= 0.9:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def column_summary(df: pd.DataFrame) -> pd.DataFrame:
    """One row per column: type, missing count, unique count."""
    return pd.DataFrame({
        "Column": df.columns,
        "Type": [str(t) for t in df.dtypes],
        "Missing": df.isna().sum().values,
        "Missing %": (df.isna().mean() * 100).round(1).values,
        "Unique": df.nunique().values,
    })


def quality_summary(df: pd.DataFrame) -> dict:
    """Headline data-quality numbers."""
    cells = df.shape[0] * df.shape[1]
    missing = int(df.isna().sum().sum())
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_cells": missing,
        "missing_pct": round(missing / cells * 100, 2) if cells else 0.0,  # avoids divide-by-zero
        "duplicate_rows": int(df.duplicated().sum()),
    }
