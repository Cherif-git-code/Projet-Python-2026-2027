import io
from pathlib import Path

import pandas as pd
import requests

URL_ECO2MIX = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-regional-cons-def/exports/csv"


def charger_eco2mix(chemin="data/raw/eco2mix_regional.parquet"):
    """Charge les données éCO2mix régionales 2021-2025.
    Si le fichier existe déjà, on le lit ; sinon on le télécharge depuis l'API ODRÉ et on l'enregistre."""
    chemin = Path(chemin)
    if chemin.exists():
        return pd.read_parquet(chemin)

    params = {
        "select": "code_insee_region,libelle_region,date_heure,consommation,nucleaire,eolien,solaire,hydraulique",
        "where": 'date_heure>="2021-01-01" and date_heure<"2026-01-01"',
    }
    reponse = requests.get(URL_ECO2MIX, params=params)
    reponse.raise_for_status()
    df = pd.read_csv(io.StringIO(reponse.text), sep=";", dtype={"eolien": str})
    df.to_parquet(chemin, index=False)
    return df
