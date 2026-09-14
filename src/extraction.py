"""Detection et chargement reproductible des fichiers sources."""
from __future__ import annotations
from pathlib import Path
import pandas as pd

def find_source_files(data_dir: Path) -> dict[str, Path]:
    """Detecte un CSV pour customers, products et sales sans le modifier."""
    found = {}
    for table in ("customers", "products", "sales"):
        matches = sorted(path for path in data_dir.glob("*.csv") if table in path.stem.lower())
        if not matches:
            raise FileNotFoundError(f"Aucun fichier CSV correspondant a '{table}' dans {data_dir}")
        found[table] = matches[0]
    return found

def load_sources(data_dir: Path) -> dict[str, pd.DataFrame]:
    """Charge les trois sources CSV."""
    return {name: pd.read_csv(path) for name, path in find_source_files(data_dir).items()}
