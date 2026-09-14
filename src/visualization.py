"""Visualisations des donnees nettoyees avec Matplotlib."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def _save_figure(figure: plt.Figure, destination: Path) -> None:
    """Enregistre et ferme une figure."""
    figure.tight_layout()
    figure.savefig(destination, dpi=150, bbox_inches="tight")
    plt.close(figure)


def plot_customers(customers: pd.DataFrame, charts_dir: Path) -> None:
    """Cree les graphiques de distribution des clients."""
    figure, axes = plt.subplots(1, 2, figsize=(11, 4))
    if "Age" in customers.columns:
        customers["Age"].dropna().plot.hist(bins=10, edgecolor="black", ax=axes[0])
    axes[0].set(title="Repartition des ages", xlabel="Age", ylabel="Nombre de clients")
    if "Gender" in customers.columns:
        customers["Gender"].value_counts().plot.bar(color="steelblue", ax=axes[1])
    axes[1].set(title="Repartition par genre", xlabel="Genre", ylabel="Nombre de clients")
    axes[1].tick_params(axis="x", rotation=0)
    _save_figure(figure, charts_dir / "customers_overview.png")


def plot_products(products: pd.DataFrame, charts_dir: Path) -> None:
    """Cree les graphiques de prix et de categories des produits."""
    figure, axes = plt.subplots(1, 2, figsize=(11, 4))
    if "Price" in products.columns:
        products["Price"].dropna().plot.box(ax=axes[0])
    axes[0].set(title="Distribution des prix", ylabel="Prix")
    if "Category" in products.columns:
        products["Category"].value_counts().plot.bar(color="darkorange", ax=axes[1])
    axes[1].set(title="Produits par categorie", xlabel="Categorie", ylabel="Nombre de produits")
    axes[1].tick_params(axis="x", rotation=35)
    _save_figure(figure, charts_dir / "products_overview.png")


def plot_sales(sales: pd.DataFrame, charts_dir: Path) -> None:
    """Cree les graphiques de chiffre d'affaires par canal et par date."""
    if not {"Quantity", "Sale_Price"}.issubset(sales.columns):
        return
    sales_with_revenue = sales.assign(Revenue=sales["Quantity"] * sales["Sale_Price"])
    figure, axes = plt.subplots(1, 2, figsize=(11, 4))
    if "Channel" in sales_with_revenue.columns:
        sales_with_revenue.groupby("Channel")["Revenue"].sum().plot.bar(color="seagreen", ax=axes[0])
    axes[0].set(title="Chiffre d'affaires par canal", xlabel="Canal", ylabel="Chiffre d'affaires")
    axes[0].tick_params(axis="x", rotation=0)
    if "Date" in sales_with_revenue.columns:
        sales_with_revenue.groupby("Date")["Revenue"].sum().sort_index().plot(marker="o", color="firebrick", ax=axes[1])
    axes[1].set(title="Chiffre d'affaires dans le temps", xlabel="Date", ylabel="Chiffre d'affaires")
    _save_figure(figure, charts_dir / "sales_overview.png")


def generate_all_visualizations(cleaned: dict[str, pd.DataFrame], output_dir: Path) -> list[str]:
    """Genere les visualisations disponibles et retourne leurs noms."""
    charts_dir = output_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)
    generated: list[str] = []
    for name, function in (("customers", plot_customers), ("products", plot_products), ("sales", plot_sales)):
        if name in cleaned:
            function(cleaned[name], charts_dir)
            generated.append(name)
    return generated
