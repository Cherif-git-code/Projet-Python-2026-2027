import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

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


def extremum_meteo(meteo, col_met, mode="max", ville=None):
    """Heure (locale, France) et valeur de l'extremum de col_met.

    mode  : "max" ou "min"
    ville : si None, un résultat par ville ; sinon, uniquement cette ville
    """
    if mode not in ("max", "min"):
        raise ValueError("mode doit valoir 'max' ou 'min'")

    df = meteo if ville is None else meteo[meteo["ville"] == ville]
    df = df.dropna(subset=[col_met])

    # Ligne de l'extremum pour chaque ville
    idx = df.groupby("ville")[col_met].agg("idxmax" if mode == "max" else "idxmin")
    res = df.loc[idx, ["ville", "time", col_met]].reset_index(drop=True)

    # time est en UTC dans meteo_pur : on le passe en heure française pour l'affichage
    if res["time"].dt.tz is not None:
        res["time"] = res["time"].dt.tz_convert("Europe/Paris")
    return res.rename(columns={col_met: "valeur"})








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
    df = meteo.copy()

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

def cumul_mensuel_precipitation(meteo,ville) :
    return (
        meteo[meteo["ville"] == ville]
        .set_index("time")["precipitation"]
        .resample("MS").sum()
    ) 


    #On prend uniquement pour une ville, on garde que précipitation et on somme par mois

#On fait l'équivalent pour les températures et la vitesse du vent
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

def vent_max_jour(meteo, ville):
    """Vitesse maximum du vent à 100 m pour chaque jour (unité de l'API, km/h par défaut)."""
    return _serie_jour(meteo, ville, "vent100_max_jour")

def precipitation_jour(meteo,ville) :
    return _serie_jour(meteo, ville, "precipitation")


















#Fonctions utiliser pour plot les fonctions précédentes


def tracer_cumul_mensuel_precipitation(meteo, ville):
    """Précipitations cumulées par mois (mm) pour une ville."""
    pluie= cumul_mensuel_precipitation(meteo,ville)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(pluie.index, pluie.values, width=25)
    ax.set_title(f"Précipitations mensuelles cumulées à {ville.capitalize()} (2021-2025)")
    ax.set_xlabel("Mois")
    ax.set_ylabel("Précipitations en mm")
    plt.show()

def tracer_temperature_moyenne_jour(meteo, ville):
    tmoy = temperature_moyenne_jour(meteo, ville)
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(tmoy.index, tmoy.values, linewidth=0.8, color="tab:blue", label="Température moyenne")
    ax.axhline(SEUIL_FROID, color="tab:cyan", linestyle="--", label=f"Seuil de froid ({SEUIL_FROID} °C, sur la moyenne)")
    ax.axhline(SEUIL_CHAUD, color="tab:red", linestyle="--", label=f"Seuil de chaleur ({SEUIL_CHAUD} °C, sur le maximum)")
    ax.set_title(f"Températures moyennes journalières à {ville.capitalize()} (2021-2025)")
    ax.set_xlabel("Date"); ax.set_ylabel("Température (°C)")
    ax.legend(loc="upper left")
    plt.show()

def tracer_temperature_max_jour(meteo,ville) :
    tmax = temperature_max_jour(meteo, ville)
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(tmax.index, tmax.values, linewidth=0.8, color="tab:orange", label="Température maximale")
    ax.axhline(SEUIL_FROID, color="tab:cyan", linestyle="--", label=f"Seuil de froid ({SEUIL_FROID} °C, sur la moyenne)")
    ax.axhline(SEUIL_CHAUD, color="tab:red", linestyle="--", label=f"Seuil de chaleur ({SEUIL_CHAUD} °C, sur le maximum)")
    ax.set_title(f"Températures maximales journalières à {ville.capitalize()} (2021-2025)")
    ax.set_xlabel("Date"); ax.set_ylabel("Température (°C)")
    ax.legend(loc="upper left")
    plt.show()

def tracer_vent_moyen_jour(meteo, ville):
    vent = vent_moyen_jour(meteo, ville)

    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(vent.index, vent.values, linewidth=0.8, color="tab:green", label="Vent moyen journalier à 100 m")
    ax.plot(vent.index, vent.rolling(30, center=True).mean(), linewidth=1.8, color="tab:red",
            label="Moyenne mobile 30 jours")
    ax.axhline(vent.mean(), color="gray", linestyle="--", label=f"Moyenne 2021-2025 ({vent.mean():.1f} km/h)")
    ax.set_title(f"Vitesse moyenne journalière du vent à 100 m à {ville.capitalize()} (2021-2025)")
    ax.set_xlabel("Date"); ax.set_ylabel("Vitesse du vent (km/h)")
    ax.legend(loc="upper left")
    plt.show()

def tracer_vent_max_jour(meteo, ville):
    vent = vent_max_jour(meteo, ville)

    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(vent.index, vent.values, linewidth=0.8, color="tab:green", label="Vent max journalier à 100 m")
    ax.plot(vent.index, vent.rolling(30, center=True).mean(), linewidth=1.8, color="tab:red",
            label="Moyenne mobile 30 jours")
    ax.axhline(vent.mean(), color="gray", linestyle="--", label=f"Moyenne 2021-2025 ({vent.mean():.1f} km/h)")
    ax.set_title(f"Vitesse max journalière du vent à 100 m à {ville.capitalize()} (2021-2025)")
    ax.set_xlabel("Date"); ax.set_ylabel("Vitesse du vent (km/h)")
    ax.legend(loc="upper left")
    plt.show()

def tracer_precipitation_jour(meteo, ville):
    pluie = precipitation_jour(meteo,ville)

    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(pluie.index, pluie.values, linewidth=0.8, color="tab:green", label="precipitation journalière")
    ax.plot(pluie.index, pluie.rolling(30, center=True).mean(), linewidth=1.8, color="tab:red",
            label="Moyenne mobile 30 jours")
    ax.axhline(pluie.mean(), color="gray", linestyle="--", label=f"Moyenne 2021-2025 ({pluie.mean():.1f} mm)")
    ax.set_title(f"Precipitation journalière à {ville.capitalize()} (2021-2025)")
    ax.set_xlabel("Date"); ax.set_ylabel("precipitation (mm)")
    ax.legend(loc="upper left")
    plt.show()