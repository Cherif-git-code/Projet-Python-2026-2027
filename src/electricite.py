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
# Une ville par région (chef-lieu), avec les mêmes noms que dans les données météo de Hugo
REGION_VERS_VILLE = {
    11: "paris", 84: "lyon", 27: "dijon", 53: "rennes",
    24: "orleans", 44: "strasbourg", 32: "lille", 28: "rouen",
    75: "bordeaux", 76: "toulouse", 52: "nantes", 93: "marseille",
}

COLONNES_ELEC = ["consommation", "nucleaire", "eolien", "solaire", "hydraulique"]


def preparer_eco2mix(df):
    """Nettoie les données éCO2mix et passe de la demi-heure à l'heure (moyenne des deux demi-heures)."""
    df = df.copy()
    df["eolien"] = pd.to_numeric(df["eolien"], errors="coerce")   # "-" devient une valeur manquante
    df["date_heure"] = pd.to_datetime(df["date_heure"], utc=True)
    df = df.dropna(subset=["consommation"])                        # la demi-heure vide du 31/12/2025 23h UTC

    df["time"] = df["date_heure"].dt.floor("h")                    # 14h30 devient 14h00
    horaire = df.groupby(["code_insee_region", "time"])[COLONNES_ELEC].mean().reset_index()

    horaire["ville"] = horaire["code_insee_region"].map(REGION_VERS_VILLE)
    return horaire
