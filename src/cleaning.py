"""Nettoyage vectorise des tables customers, products et sales."""
from __future__ import annotations
import pandas as pd
from src.validation import require_column

def _strip_text(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Supprime les espaces superflus dans les colonnes texte."""
    result = dataframe.copy()
    columns = result.select_dtypes(include=["object", "string"]).columns
    result[columns] = result[columns].apply(lambda series: series.str.strip())
    return result

def clean_customers(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Nettoie customers et ne retire que les doublons totalement identiques."""
    require_column(dataframe, "Customer_ID", "customers")
    cleaned = _strip_text(dataframe).drop_duplicates().copy()
    if "Email" in cleaned.columns:
        cleaned["Email"] = cleaned["Email"].str.lower()
    return cleaned

def clean_products(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Nettoie products et ecarte les prix manquants, nuls ou negatifs."""
    require_column(dataframe, "Product_ID", "products")
    require_column(dataframe, "Price", "products")
    cleaned = _strip_text(dataframe).drop_duplicates().copy()
    cleaned["Price"] = pd.to_numeric(cleaned["Price"], errors="coerce")
    return cleaned.loc[cleaned["Price"].notna() & cleaned["Price"].gt(0)].copy()

def clean_sales(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Nettoie sales, convertit les types et ecarte les dates/montants invalides."""
    for column in ("Sale_ID", "Customer_ID", "Product_ID", "Date", "Quantity", "Sale_Price"):
        require_column(dataframe, column, "sales")
    cleaned = _strip_text(dataframe).drop_duplicates().copy()
    cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce")
    cleaned["Quantity"] = pd.to_numeric(cleaned["Quantity"], errors="coerce")
    cleaned["Sale_Price"] = pd.to_numeric(cleaned["Sale_Price"], errors="coerce")
    valid = cleaned[["Date", "Quantity", "Sale_Price"]].notna().all(axis=1)
    valid &= cleaned["Quantity"].ge(0) & cleaned["Sale_Price"].ge(0)
    return cleaned.loc[valid].sort_values("Date", kind="stable").reset_index(drop=True)
