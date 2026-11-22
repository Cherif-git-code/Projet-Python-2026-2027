import json
from pathlib import Path
import pandas as pd

SEUIL_FROID = 15   # en dessous de 15°C, on estime que les ménages français commencent à chauffer
SEUIL_CHAUD = 27   # Pareillement au dessus de 27°C, on estime qu'ils climatisent



def charger_meteo(raw_dir):
    """Fonction qui permet de charger les données de météo dans n'importe quel notebook"""
    #raw_dir est l'emplacement des données que j'ai importé donc ici ça sera toujours "data/raw/openmeteo"
    frames = []
    for f in sorted(Path(raw_dir).glob("*.json")):
        ville, annee = f.stem.rsplit("_", 1)
        payload = json.loads(f.read_text(encoding="utf-8"))
        df = pd.DataFrame(payload["hourly"])
        df["time"] = pd.to_datetime(df["time"], utc=True)
        df["ville"] = ville
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def temp_journ(df):
    """Température moyenne par jour et par ville par jours.""" #On en a besoin car en été on a des nuits ou la température tombe sous les 15 degrés sans qu'il ne fasse froid pour autant
    jour = (
        df.set_index("time")
          .groupby("ville")["temperature_2m"]
          .resample("D").mean()
          .rename("temp_moy")
          .reset_index()
    )
    jour["sous_15"] = jour["temp_moy"] < SEUIL_FROID
    jour["sup_27"] = jour["temp_moy"] > SEUIL_CHAUD
    return jour

def preparer_meteo(meteo):
    """On retire la radiation car on en fait rien et on ajoute les indicateurs de froid et de chaleur."""
    #donc on enlève la radiation
    df = meteo.drop(columns=["shortwave_radiation"]).copy() 

    # On vérifie si la température et sous le seuil
    df["sous_15"] = df["temperature_2m"] < SEUIL_FROID
    df["sup_27"] = df["temperature_2m"] > SEUIL_CHAUD

    # On vérifie à quel point la température est sous le seuil
    df["deg_sous_15"] = (SEUIL_FROID - df["temperature_2m"]).clip(lower=0)
    df["deg_sup_27"] = (df["temperature_2m"] - SEUIL_CHAUD).clip(lower=0)
    return df

def cumul_mensuel(meteo, ville):
    """Précipitations cumulées par mois (mm) pour une ville."""
    return (
        meteo[meteo["ville"] == ville]
        .set_index("time")["precipitation"]
        .resample("MS").sum()
    )