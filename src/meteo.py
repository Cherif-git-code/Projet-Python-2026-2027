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
    """Nettoie et enrichit le tableau météo.

    - convertit l'horodatage UTC en heure française
    - ajoute les indicateurs horaires et journaliers de froid et de chaleur
    """
    df = meteo

    # Conversion UTC -> heure française
    df["time"] = df["time"].dt.tz_convert("Europe/Paris")

    # Retire l'heure qui déborde sur 2026 (31/12/2025 23 h UTC = 01/01/2026 0 h locale)
    df = df[df["time"].dt.year <= 2025].copy()

    df["jour"] = df["time"].dt.date                  # date seule, sans heure

    # Indicateurs horaires
    df["sous_15"] = df["temperature_2m"] < SEUIL_FROID
    df["sup_27"] = df["temperature_2m"] > SEUIL_CHAUD

    # Intensité (optionnel)
    df["deg_sous_15"] = (SEUIL_FROID - df["temperature_2m"]).clip(lower=0)
    df["deg_sup_27"] = (df["temperature_2m"] - SEUIL_CHAUD).clip(lower=0)

    # Indicateurs journaliers (valeur répétée sur toutes les heures du jour)
    par_jour = df.groupby(["ville", "jour"])["temperature_2m"]
    df["tmax_jour"] = par_jour.transform("max")
    df["tmoy_jour"] = par_jour.transform("mean")
    df["jour_chaud"] = df["tmax_jour"] > SEUIL_CHAUD
    df["jour_froid"] = df["tmoy_jour"] < SEUIL_FROID
    
    #Indicateur journalier de la vitesse moyenne du vent à 100m 
    df["vent100_moy_jour"] = df.groupby(["ville", "jour"])["wind_speed_100m"].transform("mean")
    df["vent100_max_jour"] = df.groupby(["ville", "jour"])["wind_speed_100m"].transform("max")
    return df

def cumul_mensuel(meteo, ville):
    """Précipitations cumulées par mois (mm) pour une ville."""
    return (
        meteo[meteo["ville"] == ville]
        .set_index("time")["precipitation"]
        .resample("MS").sum()
    ) #On prend uniquement pour une ville, on garde que précipitation et on somme par mois

#On fait l'équivalent pour les températures
def _serie_jour(meteo, ville, colonne):
    """Une valeur par jour pour une ville, indexée par une vraie date."""
    j = meteo[meteo["ville"] == ville].drop_duplicates("jour")
    return j.set_index(pd.to_datetime(j["jour"]))[colonne].sort_index()


def temperature_moyenne_jour(meteo, ville):
    """Température moyenne de chaque jour (°C)."""
    return _serie_jour(meteo, ville, "tmoy_jour")


def temperature_max_jour(meteo, ville):
    """Température maximale de chaque jour (°C)."""
    return _serie_jour(meteo, ville, "tmax_jour")

def vent_moyen_jour(meteo, ville):
    """Vitesse moyenne du vent à 100 m pour chaque jour (unité de l'API, km/h par défaut)."""
    return _serie_jour(meteo, ville, "vent100_moy_jour")