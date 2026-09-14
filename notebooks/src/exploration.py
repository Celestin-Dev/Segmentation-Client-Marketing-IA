"""Fonctions d'exploration initiale des jeux de donnees."""

from __future__ import annotations

from datetime import datetime

import pandas as pd


def log(message: str) -> None:
    # Affiche un message avec la date et l'heure.
    """Affiche un message horodate pour le suivi du pipeline."""
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}")


def explore_dataframe(dataframe: pd.DataFrame, dataset_name: str) -> None:
    # Montre les informations principales du fichier.
    """Affiche les indicateurs essentiels de qualite d'un jeu de donnees.

    Args:
        dataframe: Jeu de donnees a analyser.
        dataset_name: Nom lisible du jeu de donnees pour les journaux.
    """
    log(f"Exploration de '{dataset_name}' : {dataframe.shape[0]} lignes, "
        f"{dataframe.shape[1]} colonnes.")
    print("Colonnes :", ", ".join(dataframe.columns))
    print("Types :")
    print(dataframe.dtypes.to_string())
    print("Valeurs manquantes :")
    print(dataframe.isna().sum().to_string())
    print(f"Lignes dupliquees : {dataframe.duplicated().sum()}")
    print()
