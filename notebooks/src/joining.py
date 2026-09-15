"""Verification relationnelle et jointure des tables nettoyees."""
from __future__ import annotations
import pandas as pd

def relationship_report(customers: pd.DataFrame, products: pd.DataFrame, sales: pd.DataFrame) -> dict[str, int]:
    """Compte les doublons de cles et les cles etrangeres orphelines."""
    return {"customer_primary_key_duplicates": int(customers["Customer_ID"].duplicated().sum()), "product_primary_key_duplicates": int(products["Product_ID"].duplicated().sum()), "sales_unknown_customers": int((~sales["Customer_ID"].isin(customers["Customer_ID"])).sum()), "sales_unknown_products": int((~sales["Product_ID"].isin(products["Product_ID"])).sum())}

def build_dataset_clean(customers: pd.DataFrame, products: pd.DataFrame, sales: pd.DataFrame) -> pd.DataFrame:
    """Joint sales aux dimensions uniques sans multiplication de lignes."""
    if customers["Customer_ID"].duplicated().any() or products["Product_ID"].duplicated().any():
        raise ValueError("Jointure annulee : une cle primaire n'est pas unique.")
    result = sales.merge(products, on="Product_ID", how="left", validate="many_to_one", suffixes=("", "_product"))
    result = result.merge(customers, on="Customer_ID", how="left", validate="many_to_one", suffixes=("", "_customer"))
    result["Revenue"] = result["Quantity"] * result["Sale_Price"]
    if len(result) != len(sales):
        raise ValueError("La jointure a modifie le nombre de lignes de ventes.")
    return result
