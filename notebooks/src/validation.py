from __future__ import annotations

import pandas as pd


def require_column(dataframe: pd.DataFrame, column: str, dataset_name: str) -> None:
    """Leve une erreur explicite lorsqu'une colonne obligatoire est absente."""
    if column not in dataframe.columns:
        raise KeyError(
            f"Colonne obligatoire '{column}' absente du fichier {dataset_name}. "
            f"Colonnes disponibles : {', '.join(dataframe.columns)}"
        )