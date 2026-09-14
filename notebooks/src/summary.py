"""Production de resumes metiers pour les donnees nettoyees."""
from __future__ import annotations
import pandas as pd


def build_summary(dataframes: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Retourne les indicateurs generaux et metiers de chaque jeu de donnees."""
    rows: list[dict[str, object]] = []
    for name, dataframe in dataframes.items():
        row: dict[str, object] = {"dataset": name, "rows": len(dataframe), "columns": len(dataframe.columns), "missing_values": int(dataframe.isna().sum().sum()), "duplicate_rows": int(dataframe.duplicated().sum()), "metric": "", "value": ""}
        rows.append(row)
        if name == "customers" and "Total_Spent" in dataframe:
            rows.append({**row, "metric": "total_spent", "value": dataframe["Total_Spent"].sum()})
        elif name == "products" and "Price" in dataframe:
            rows.append({**row, "metric": "average_price", "value": dataframe["Price"].mean()})
        elif name == "sales" and {"Quantity", "Sale_Price"}.issubset(dataframe.columns):
            rows.append({**row, "metric": "revenue", "value": (dataframe["Quantity"] * dataframe["Sale_Price"]).sum()})
    return pd.DataFrame(rows)
